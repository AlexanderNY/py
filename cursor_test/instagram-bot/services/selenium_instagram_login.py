"""Авторизация в Instagram через Selenium (веб-форма) — fallback при сбое instagrapi."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from selenium.common.exceptions import TimeoutException as SeleniumTimeout
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from services.selenium_driver import create_chrome_driver
from services.selenium_diag_storage import try_capture_and_upload_diag

logger = logging.getLogger(__name__)

LOGIN_URL = "https://www.instagram.com/accounts/login/"


@dataclass
class SeleniumInstagramLoginResult:
    ok: bool
    status: str  # success | challenge | failed | error
    message: str
    cookie_dict: Optional[Dict[str, str]] = None
    # Ключ в S3 (имя файла содержит diag), если сохранён скрин при ошибке
    diagnostic_s3_key: Optional[str] = None


def _fail_with_diag(
    driver: Any,
    status: str,
    message: str,
    reason_slug: str,
) -> SeleniumInstagramLoginResult:
    diag = try_capture_and_upload_diag(driver, reason_slug)
    return SeleniumInstagramLoginResult(
        ok=False,
        status=status,
        message=message,
        diagnostic_s3_key=diag,
    )


def _instagram_cookie_dict_from_driver(driver: Any) -> Dict[str, str]:
    raw = driver.get_cookies()
    out: Dict[str, str] = {}
    for c in raw:
        domain = (c.get("domain") or "").lower()
        if "instagram.com" not in domain:
            continue
        name = c.get("name")
        if name:
            out[str(name)] = str(c.get("value", ""))
    return out


def _dismiss_common_modals(driver: Any) -> None:
    for _ in range(3):
        for xpath in (
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), 'Not now')]",
        ):
            try:
                for el in driver.find_elements(By.XPATH, xpath)[:2]:
                    if el.is_displayed():
                        el.click()
                        time.sleep(0.4)
            except Exception:
                pass
        time.sleep(0.25)


def attempt_instagram_login_via_selenium(username: str, password: str) -> SeleniumInstagramLoginResult:
    """
    Открывает страницу логина, вводит учётные данные, отправляет форму.
    При успехе возвращает cookie_dict для переноса в instagrapi.
    """
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        return SeleniumInstagramLoginResult(
            ok=False,
            status="error",
            message="username_and_password_required",
        )

    timeout = max(30, int(getattr(settings, "SELENIUM_INSTAGRAM_LOGIN_TIMEOUT_SEC", 120)))
    driver = None
    try:
        driver = create_chrome_driver()
        driver.get(LOGIN_URL)

        wait_short = WebDriverWait(driver, min(45, timeout))
        try:
            user_el = wait_short.until(EC.presence_of_element_located((By.NAME, "username")))
        except SeleniumTimeout:
            return _fail_with_diag(driver, "failed", "login_form_not_found", "login_form_not_found")

        user_el.clear()
        user_el.send_keys(username)
        pass_el = driver.find_element(By.NAME, "password")
        pass_el.clear()
        pass_el.send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            url = (driver.current_url or "").lower()
            if "challenge" in url or "checkpoint" in url:
                return _fail_with_diag(
                    driver,
                    "challenge",
                    "instagram_challenge_or_checkpoint_requires_manual_step",
                    "challenge_in_loop",
                )
            cookies = _instagram_cookie_dict_from_driver(driver)
            if cookies.get("sessionid") and cookies.get("ds_user_id"):
                _dismiss_common_modals(driver)
                cookies = _instagram_cookie_dict_from_driver(driver)
                return SeleniumInstagramLoginResult(
                    ok=True,
                    status="success",
                    message="web_login_ok",
                    cookie_dict=cookies,
                )
            time.sleep(1.0)

        url = (driver.current_url or "").lower()
        if "challenge" in url or "checkpoint" in url:
            return _fail_with_diag(
                driver,
                "challenge",
                "instagram_challenge_or_checkpoint_requires_manual_step",
                "challenge_after_wait",
            )
        return _fail_with_diag(
            driver,
            "failed",
            "timeout_waiting_for_session_cookies",
            "timeout_session_cookies",
        )
    except Exception as e:
        logger.exception("Selenium Instagram login error: %s", e)
        diag = try_capture_and_upload_diag(driver, "exception") if driver is not None else None
        return SeleniumInstagramLoginResult(
            ok=False,
            status="error",
            message=f"{type(e).__name__}: {e}",
            diagnostic_s3_key=diag,
        )
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception as e:
                logger.warning("driver.quit(): %s", e)
