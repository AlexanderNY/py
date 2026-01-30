"""Опрос core, сохранение снимков и оповещение ботов."""

import asyncio
import hashlib
import json
import logging
from typing import Any

import httpx

from config import settings
from database import get_db_connection

logger = logging.getLogger(__name__)

BOT_PLATFORMS = ["tg", "wp", "vk", "url"]


def _payload_hash(schedules: list[dict[str, Any]]) -> str:
    raw = json.dumps(schedules, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


async def _login() -> str:
    base = settings.API_GATEWAY_URL.rstrip("/")
    url = f"{base}/auth/login"
    payload = {
        "username": settings.SCHEDULER_LOGIN or "",
        "password": settings.SCHEDULER_PASSWORD or "",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"Login failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["access_token"]


async def _fetch_schedules(token: str) -> list[dict[str, Any]]:
    base = settings.API_GATEWAY_URL.rstrip("/")
    url = f"{base}/core/schedules"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
    if resp.status_code == 401:
        raise RuntimeError("Unauthorized")
    resp.raise_for_status()
    data = resp.json()
    return data.get("schedules") or []


async def _fetch_profiles_parallel(token: str) -> dict[str, list[dict[str, Any]]]:
    """Параллельно получает все профили через API Gateway.
    
    Args:
        token: JWT токен авторизации
        
    Returns:
        Словарь с данными профилей по платформам:
        {
            "wp": [...],
            "tg": [...],
            "tw": [...],
            "vk": [...]
        }
    """
    base = settings.API_GATEWAY_URL.rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}
    
    async def fetch_platform_profiles(platform: str) -> tuple[str, list[dict[str, Any]]]:
        """Получает профили для одной платформы."""
        url = f"{base}/{platform}/profiles"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 401:
                    raise RuntimeError("Unauthorized")
                resp.raise_for_status()
                data = resp.json()
                return platform, data.get("profiles") or []
        except Exception as e:
            logger.warning("Failed to fetch %s profiles: %s", platform, e)
            return platform, []
    
    # Параллельный запрос всех платформ
    results = await asyncio.gather(
        fetch_platform_profiles("wp"),
        fetch_platform_profiles("tg"),
        fetch_platform_profiles("tw"),
        fetch_platform_profiles("vk"),
        return_exceptions=True
    )
    
    # Собираем результаты в словарь
    profiles_data = {}
    for result in results:
        if isinstance(result, Exception):
            logger.error("Error fetching profiles: %s", result)
            continue
        platform, profiles = result
        profiles_data[platform] = profiles
    
    return profiles_data


def _transform_profiles_to_schedules(profiles_data: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Преобразует данные профилей в формат расписаний.
    
    Args:
        profiles_data: Словарь с профилями по платформам
        
    Returns:
        Список расписаний в формате:
        {
            "user_id": int,
            "platform": str,
            "publish_enabled": bool,
            "collect_enabled": bool,
            "schedule_type": str,
            "time_intervals": list
        }
    """
    schedules = []
    
    for platform, profiles in profiles_data.items():
        for profile in profiles:
            # Парсим time_intervals: строка "HH:MM" или JSON-массив
            time_intervals = profile.get("time_intervals", [])
            if isinstance(time_intervals, str):
                if time_intervals and ":" in time_intervals and len(time_intervals) <= 5:
                    time_intervals = [{"start": time_intervals, "end": time_intervals}]
                else:
                    try:
                        time_intervals = json.loads(time_intervals) if time_intervals else []
                    except json.JSONDecodeError:
                        time_intervals = []
            
            schedule = {
                "user_id": profile.get("user_id"),
                "platform": platform,
                "publish_enabled": bool(profile.get("publish_enabled", False)),
                "collect_enabled": bool(profile.get("collect_enabled", False)),
                "schedule_type": profile.get("schedule_type") or "immediate",
                "time_intervals": time_intervals if isinstance(time_intervals, list) else []
            }
            schedules.append(schedule)
    
    return schedules


async def _load_previous_snapshot() -> list[dict[str, Any]]:
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT user_id, platform, publish_enabled, collect_enabled, schedule_type, time_intervals FROM schedule_snapshots"
            )
            rows = await cur.fetchall()
            cols = ["user_id", "platform", "publish_enabled", "collect_enabled", "schedule_type", "time_intervals"]
        out = []
        for row in rows:
            rec = dict(zip(cols, row))
            ti = rec.get("time_intervals")
            if isinstance(ti, str):
                try:
                    ti = json.loads(ti) if ti else []
                except json.JSONDecodeError:
                    ti = []
            rec["time_intervals"] = ti
            out.append(rec)
        return out


async def _store_snapshot(schedules: list[dict[str, Any]]) -> None:
    async with get_db_connection() as conn:
        cur = await conn.cursor()
        try:
            # Начинаем транзакцию через SQL
            await cur.execute("BEGIN")
            await cur.execute("DELETE FROM schedule_snapshots")
            for s in schedules:
                ti = json.dumps(s.get("time_intervals") or [])
                await cur.execute(
                    """
                    INSERT INTO schedule_snapshots (
                        user_id, platform, publish_enabled, collect_enabled,
                        schedule_type, time_intervals, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    (
                        s["user_id"],
                        s["platform"],
                        s.get("publish_enabled", False),
                        s.get("collect_enabled", False),
                        s.get("schedule_type") or "immediate",
                        ti,
                    ),
                )
            # Коммитим транзакцию через SQL
            await cur.execute("COMMIT")
        except Exception:
            # Откатываем транзакцию через SQL
            await cur.execute("ROLLBACK")
            raise
        finally:
            cur.close()


async def _notify_bot(platform: str, schedules: list[dict[str, Any]], token: str) -> None:
    base = settings.API_GATEWAY_URL.rstrip("/")
    url = f"{base}/{platform}-bot/schedule"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"schedules": schedules}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
    if resp.status_code >= 400:
        logger.warning("Notify %s failed: %s %s", platform, resp.status_code, resp.text)
        return
    logger.info("Notified %s: %d schedules", platform, len(schedules))


async def run_poll_cycle(token: str) -> bool:
    """Один цикл: запрос core, diff, сохранение, оповещение. Возвращает True если были изменения."""
    schedules = await _fetch_schedules(token)
    new_h = _payload_hash(schedules)
    try:
        prev = await _load_previous_snapshot()
        old_h = _payload_hash(prev)
    except Exception:
        old_h = None
    changed = old_h != new_h
    await _store_snapshot(schedules)

    if not settings.NOTIFY_ON_CHANGE_ONLY or changed:
        by_platform: dict[str, list[dict[str, Any]]] = {p: [] for p in BOT_PLATFORMS}
        for s in schedules:
            p = s.get("platform")
            if p in by_platform:
                by_platform[p].append(s)
        for platform in BOT_PLATFORMS:
            await _notify_bot(platform, by_platform[platform], token)

    return changed


def _has_login_credentials() -> bool:
    return bool(settings.SCHEDULER_LOGIN and settings.SCHEDULER_PASSWORD)


async def poll_loop() -> None:
    token: str | None = settings.SCHEDULER_JWT
    if not token and _has_login_credentials():
        try:
            token = await _login()
        except Exception as e:
            logger.error("Initial login failed: %s", e)
            return

    while True:
        try:
            if not token and _has_login_credentials():
                token = await _login()
            if token:
                await run_poll_cycle(token)
        except RuntimeError as e:
            if ("Unauthorized" in str(e) or "401" in str(e)) and _has_login_credentials():
                token = None
                logger.warning("Will re-login on next cycle")
            else:
                logger.exception("Poll cycle error: %s", e)
        except Exception as e:
            logger.exception("Poll cycle error: %s", e)

        await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)
