"""Проверка входа Яндекс и чтение списка подписок Дзена через Selenium."""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from database import get_db_connection, release_db_connection

from .selenium_diag import capture_selenium_error_to_s3
from .selenium_driver import create_chrome_driver
from .selenium_errors import format_selenium_exception
from .yandex_auth import YandexAuthError, ensure_dzen_session, login_yandex_passport

logger = logging.getLogger(__name__)

# Ссылки на каналы/паблишеров в ленте подписок
_HREF_CHANNEL = re.compile(
    r"https?://(?:www\.)?dzen\.ru/(?:id/[^/?#]+|media/id/[^/?#]+|profile/[^/?#]+)(?:/|$|\?)",
    re.IGNORECASE,
)


def _normalize_href(raw: str) -> str:
    if not raw:
        return ""
    s = raw.strip()
    if s.startswith("//"):
        s = "https:" + s
    if s.startswith("/"):
        s = "https://dzen.ru" + s
    return s


def _link_title(el) -> str:
    try:
        t = (el.text or "").strip()
        if t:
            return t[:500]
        t2 = el.get_attribute("title") or el.get_attribute("aria-label") or ""
        return (t2 or "").strip()[:500]
    except Exception:
        return ""


def _collect_subscription_links(driver: WebDriver) -> List[Dict[str, str]]:
    """Собирает уникальные ссылки на каналы со страницы подписок."""
    seen: set[str] = set()
    out: List[Dict[str, str]] = []

    selectors = [s.strip() for s in settings.DZEN_SUBSCRIPTIONS_LINK_SELECTORS.split(",") if s.strip()]
    elements: List[object] = []
    for sel in selectors:
        try:
            found = driver.find_elements(By.CSS_SELECTOR, sel)
            if found:
                elements.extend(found)
        except Exception:
            continue

    if not elements:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='dzen.ru']")
        except Exception:
            elements = []

    for el in elements:
        try:
            href = el.get_attribute("href") or ""
            href = _normalize_href(href)
            if not href or "passport.yandex" in href:
                continue
            if not _HREF_CHANNEL.search(href):
                continue
            parsed = urlparse(href)
            path = (parsed.path or "").rstrip("/")
            key = f"{parsed.netloc}{path}"
            if key in seen:
                continue
            seen.add(key)
            title = _link_title(el) or path.split("/")[-1] or href
            out.append({"title": title, "url": href})
        except Exception:
            continue

    return out


def _scroll_page(driver: WebDriver, times: int = 3) -> None:
    for _ in range(max(1, times)):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(float(settings.DZEN_SUBSCRIPTIONS_SCROLL_PAUSE_SEC))
        except Exception:
            break


def verify_subscriptions_sync(
    login: str, password: str, user_id: Optional[int] = None
) -> Tuple[bool, List[Dict[str, str]], Optional[str]]:
    """
    Вход и переход на страницу подписок; возвращает (ok, subscriptions, error_message).
    При ok=True error_message может быть предупреждением (пустой список).
    """
    login = (login or "").strip()
    password = (password or "").strip()
    if not login or not password:
        return False, [], "Не заданы логин или пароль в профиле Дзен"

    driver: Optional[WebDriver] = None
    try:
        driver = create_chrome_driver()
        login_yandex_passport(driver, login, password)
        ensure_dzen_session(driver)

        url = (settings.DZEN_SUBSCRIPTIONS_URL or "").strip() or "https://dzen.ru/subscriptions"
        driver.get(url)
        time.sleep(2.0)

        wait_sec = max(15, int(settings.DZEN_SUBSCRIPTIONS_WAIT_SEC))
        WebDriverWait(driver, wait_sec).until(lambda d: d.find_element(By.TAG_NAME, "body"))

        cur = (driver.current_url or "").lower()
        if "passport.yandex" in cur and "session" not in cur:
            return False, [], "Редирект на Passport: сессия Дзена не подтверждена"

        time.sleep(2.0)
        _scroll_page(driver, settings.DZEN_SUBSCRIPTIONS_SCROLL_TIMES)

        subs = _collect_subscription_links(driver)
        if not subs:
            # Повтор после дополнительного ожидания (ленивая подгрузка)
            time.sleep(3.0)
            _scroll_page(driver, 2)
            subs = _collect_subscription_links(driver)

        warn: Optional[str] = None
        if not subs:
            warn = (
                "Вход выполнен, но подписки на странице не распознаны "
                "(пустой список или изменилась вёрстка Дзена)."
            )
            logger.info("Dzen subscriptions probe: 0 items parsed for login=%s", login[:3] + "***")

        return True, subs, warn
    except YandexAuthError as e:
        logger.warning("Dzen subscriptions probe: %s", e)
        capture_selenium_error_to_s3(driver, "subscriptions_probe_yandex_auth", user_id=user_id)
        return False, [], str(e)
    except Exception as e:
        friendly = format_selenium_exception(e)
        capture_selenium_error_to_s3(driver, "subscriptions_probe_exception", user_id=user_id)
        logger.exception("Dzen subscriptions probe failed: %s", friendly)
        return False, [], friendly
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


async def fetch_yandex_credentials(user_id: int) -> Tuple[Optional[str], Optional[str]]:
    """Читает логин и пароль из БД (как в publisher)."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT yandex_login, yandex_password
                FROM dzen_profiles
                WHERE user_id = %s
                """,
                (user_id,),
            )
            row = await cur.fetchone()
            if not row:
                return None, None
            login = (row[0] or "").strip() if row[0] else None
            password = (row[1] or "").strip() if row[1] else None
            return login, password
    finally:
        await release_db_connection(conn)


async def set_last_auth_error(user_id: int, message: Optional[str]) -> None:
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE dzen_profiles SET last_auth_error = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """,
                (message, user_id),
            )
    finally:
        await release_db_connection(conn)


async def verify_yandex_for_user(user_id: int) -> Dict[str, Any]:
    """Проверка по сохранённым в БД учётным данным."""
    import asyncio

    login, password = await fetch_yandex_credentials(user_id)
    if not login or not password:
        err = "Сохраните логин и пароль Яндекса во вкладке «Авторизация» (профиль Дзен)."
        await set_last_auth_error(user_id, err)
        return {"ok": False, "subscriptions": [], "error": err}

    ok, subs, msg = await asyncio.to_thread(verify_subscriptions_sync, login, password, user_id)

    if ok:
        await set_last_auth_error(user_id, None)
        result: Dict[str, Any] = {"ok": True, "subscriptions": subs}
        if msg:
            result["message"] = msg
        return result

    err_text = (msg or "Ошибка проверки авторизации")[:2000]
    await set_last_auth_error(user_id, err_text)
    return {"ok": False, "subscriptions": [], "error": err_text}
