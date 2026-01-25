"""Сервис агрегации расписаний из профилей платформ."""

import json
from typing import Any

from database import get_db_connection


class SchedulesService:
    """Агрегирует schedule-relevant поля из tg/tw/wp/vk_profiles."""

    PLATFORMS = [
        ("tg_profiles", "tg"),
        ("tw_profiles", "tw"),
        ("wp_profiles", "wp"),
        ("vk_profiles", "vk"),
    ]

    async def get_all_schedules(self) -> list[dict[str, Any]]:
        """Собирает расписания из всех таблиц профилей.

        Returns:
            Список записей {user_id, platform, publish_enabled, collect_enabled,
            schedule_type, time_intervals}.
        """
        result: list[dict[str, Any]] = []
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                for table, platform in self.PLATFORMS:
                    await cur.execute(
                        f"""
                        SELECT user_id, publish_enabled, collect_enabled,
                               schedule_type, time_intervals
                        FROM {table}
                        """
                    )
                    rows = await cur.fetchall()
                    desc = cur.description
                    cols = [c.name for c in desc] if desc else []
                    for row in rows:
                        rec = dict(zip(cols, row))
                        ti = rec.get("time_intervals")
                        if isinstance(ti, str):
                            try:
                                ti = json.loads(ti) if ti else []
                            except json.JSONDecodeError:
                                ti = []
                        result.append({
                            "user_id": rec["user_id"],
                            "platform": platform,
                            "publish_enabled": bool(rec.get("publish_enabled", False)),
                            "collect_enabled": bool(rec.get("collect_enabled", False)),
                            "schedule_type": rec.get("schedule_type") or "immediate",
                            "time_intervals": ti if isinstance(ti, list) else [],
                        })
        finally:
            conn.close()
        return result


schedules_service = SchedulesService()
