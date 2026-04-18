"""
Синхронный сценарий веб-входа Meta (Facebook login).
Не извлекает Graph API token и не заменяет OAuth для Threads API.
Пароль не пишется в логи; селекторы могут устареть при смене верстки Meta.
При сбоях возвращает diagnostic_png для загрузки в S3 (ключ с подстрокой diag).
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional, Tuple

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from config import settings

logger = logging.getLogger(__name__)


def _find_first(driver: WebDriver, selectors: list[Tuple[str, str]]):
    for by, value in selectors:
        try:
            el = driver.find_element(by, value)
            if el and el.is_displayed():
                return el
        except WebDriverException:
            continue
    return None


def _capture_diag_png(driver: Optional[WebDriver]) -> Optional[bytes]:
    """PNG скриншот окна браузера для диагностики (без пароля в содержимом)."""
    if not driver:
        return None
    try:
        return driver.get_screenshot_as_png()
    except Exception:
        logger.warning("Meta selenium: get_screenshot_as_png failed", exc_info=True)
        return None


def _detect_post_login_state(driver: WebDriver) -> Tuple[str, str]:
    """Возвращает (код_статуса, сообщение_для_пользователя)."""
    url = (driver.current_url or "").lower()
    src = (driver.page_source or "").lower()

    if "checkpoint" in url or "checkpoint" in src[:8000]:
        return "challenge_required", "Meta запросила проверку (checkpoint). Завершите вход вручную в браузере."
    if "two_factor" in url or "two_step_verification" in url:
        return "challenge_required", "Требуется двухфакторная аутентификация. Выполните шаг вручную."
    if "login" in url and ("error" in src or "incorrect" in src or "wrong" in src):
        return "failed", "Не удалось войти (проверьте логин и пароль)."
    if "facebook.com" in url and "login" not in url and "checkpoint" not in url:
        return (
            "completed_unverified",
            "Браузер покинул страницу логина. Это не заменяет OAuth: для API Threads по-прежнему нужен «Connect with Threads».",
        )
    return "failed", "Не удалось определить результат входа (изменилась вёрстка Meta или таймаут)."


def run_meta_web_login(
    username: str,
    password: str,
    user_id: int,
    session_id: int,
) -> dict[str, Any]:
    """
    Пытается ввести учётные данные на странице входа Meta.
    Пароль не пишется в логи.
    При ошибках Selenium в ответе может быть diagnostic_png (bytes) для S3.
    """
    _ = user_id, session_id  # для отладки/расширений; ключ S3 формируется в upload-слое
    if not username or not password:
        return {"status": "failed", "message": "Пустой логин или пароль", "diagnostic_png": None}

    from services.selenium_driver import create_chrome_driver

    driver: Optional[WebDriver] = None

    def finish(
        status: str,
        message: str,
        *,
        diag: bool = False,
    ) -> dict[str, Any]:
        png: Optional[bytes] = None
        if diag and driver:
            png = _capture_diag_png(driver)
        return {"status": status, "message": message, "diagnostic_png": png}

    try:
        driver = create_chrome_driver()
        driver.get(settings.META_WEB_LOGIN_URL)
        wait = WebDriverWait(driver, 25)

        email_selectors = [
            (By.ID, "email"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='text'][name='email']"),
            (By.CSS_SELECTOR, "input[name='email']"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
        ]
        try:
            el_email = wait.until(lambda d: _find_first(d, email_selectors))
        except TimeoutException:
            logger.warning("Meta selenium: email field timeout")
            return finish(
                "failed",
                "Не найдено поле email (обновите селекторы или откройте Meta вручную).",
                diag=True,
            )
        if not el_email:
            return finish("failed", "Поле email не найдено.", diag=True)
        el_email.clear()
        el_email.send_keys(username)
        time.sleep(0.4)

        pwd_selectors = [
            (By.ID, "pass"),
            (By.NAME, "pass"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.NAME, "password"),
        ]
        el_pass = _find_first(driver, pwd_selectors)
        if not el_pass:
            el_pass = wait.until(lambda d: _find_first(d, pwd_selectors))
        el_pass.clear()
        el_pass.send_keys(password)

        submit = _find_first(
            driver,
            [
                (By.NAME, "login"),
                (By.CSS_SELECTOR, "button[name='login']"),
                (By.XPATH, "//button[@type='submit']"),
            ],
        )
        if submit:
            submit.click()
        else:
            el_pass.send_keys(Keys.RETURN)

        time.sleep(4.0)
        code, msg = _detect_post_login_state(driver)
        if code in ("failed", "challenge_required"):
            png = _capture_diag_png(driver)
            return {"status": code, "message": msg, "diagnostic_png": png}
        return {"status": code, "message": msg, "diagnostic_png": None}

    except TimeoutException as e:
        logger.warning("Meta selenium timeout: %s", e)
        png = _capture_diag_png(driver)
        return {
            "status": "failed",
            "message": "Таймаут при загрузке или вводе (Meta могла изменить страницу).",
            "diagnostic_png": png,
        }
    except WebDriverException as e:
        logger.warning("Meta selenium webdriver error: %s", e)
        png = _capture_diag_png(driver)
        return {
            "status": "failed",
            "message": "Ошибка браузера при входе. Проверьте Chrome/Chromium в контейнере.",
            "diagnostic_png": png,
        }
    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                pass
