"""Вход в аккаунт Яндекс через веб-интерфейс Passport."""

from __future__ import annotations

import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import settings

logger = logging.getLogger(__name__)


class YandexAuthError(Exception):
    """Не удалось войти (капча, 2FA, неверный пароль и т.д.)."""


def _find_first(driver, selectors: list[tuple[str, str]]):
    for by, value in selectors:
        try:
            el = driver.find_element(by, value)
            if el:
                return el
        except Exception:
            continue
    return None


def login_yandex_passport(driver, login: str, password: str) -> None:
    """
    Открывает Passport и вводит логин/пароль.
    Селекторы Яндекс периодически меняются — при сбоях обновить список ниже.
    """
    if not login or not password:
        raise YandexAuthError("Пустой логин или пароль")

    driver.get(settings.YANDEX_PASSPORT_URL)
    wait = WebDriverWait(driver, 30)

    login_selectors = [
        (By.ID, "passp-field-login"),
        (By.NAME, "login"),
        (By.CSS_SELECTOR, "input[type='text'][name='login']"),
        (By.CSS_SELECTOR, "input[name='login']"),
    ]
    el_login = wait.until(lambda d: _find_first(d, login_selectors))
    el_login.clear()
    el_login.send_keys(login)
    time.sleep(0.3)

    submit_login = _find_first(
        driver,
        [
            (By.ID, "passp:sign-in"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(., 'Войти') or contains(., 'Далее')]"),
        ],
    )
    if submit_login:
        submit_login.click()
    time.sleep(1.5)

    pwd_selectors = [
        (By.ID, "passp-field-passwd"),
        (By.NAME, "passwd"),
        (By.CSS_SELECTOR, "input[type='password']"),
    ]
    wait_pwd = WebDriverWait(driver, 25)
    el_pwd = wait_pwd.until(lambda d: _find_first(d, pwd_selectors))
    el_pwd.clear()
    el_pwd.send_keys(password)

    submit_pass = _find_first(
        driver,
        [
            (By.ID, "passp:sign-in"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(., 'Войти')]"),
        ],
    )
    if submit_pass:
        submit_pass.click()

    time.sleep(3.0)

    url = (driver.current_url or "").lower()
    page = (driver.page_source or "").lower()
    if "challenge" in url or "подтвердите" in page or "captcha" in page:
        raise YandexAuthError("Требуется дополнительная проверка (капча/SMS). Выполните вход вручную в профиле с персистентным браузером.")
    if "passport.yandex.ru/auth" in url and "session" not in url:
        # всё ещё на странице логина
        err_el = _find_first(
            driver,
            [
                (By.CSS_SELECTOR, ".passp-form-field__error"),
                (By.CSS_SELECTOR, "[role='alert']"),
            ],
        )
        msg = err_el.text.strip() if err_el is not None else "Не удалось войти (проверьте логин и пароль)."
        raise YandexAuthError(msg or "Ошибка авторизации Яндекс.")


def ensure_dzen_session(driver) -> None:
    """Открывает Дзен, чтобы проверить сессию после Passport."""
    driver.get("https://dzen.ru/")
    time.sleep(2.0)
