"""
Вход через dzen.ru: кнопки «Войти» → «Войти через Яндекс ID» → при необходимости «Почта» и логин, пароль.
При экране пуша — возвращаем 'push' без raise (драйвер остаётся на стороне вызывающего кода).
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, List, Literal, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings

from .yandex_auth import YandexAuthError, _find_first, _safe_page_hint

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

DzenFlowResult = Literal["ok", "push"]


def _lower_src(driver: "WebDriver", max_len: int = 400_000) -> str:
    try:
        return (driver.page_source or "")[:max_len].lower()
    except Exception:
        return ""


def _detect_captcha_block(driver: "WebDriver") -> bool:
    try:
        title = (driver.title or "").lower()
    except Exception:
        title = ""
    src = _lower_src(driver)
    markers = (
        "не робот",
        "не робот?",
        "smartcaptcha",
        "captcha by yandex",
        "подтвердите, что запросы",
        "подтвердите, что",
        "я не робот",
    )
    if any(m in src for m in markers):
        return True
    if "робот" in title and "?" in title:
        return True
    return False


def _wait_click(driver: "WebDriver", by, value: str, timeout: float) -> bool:
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
        el.click()
        return True
    except Exception:
        return False


def _click_voyti_on_dzen(driver: "WebDriver", timeout: float) -> None:
    """Кнопка/ссылка «Войти» на главной Дзена."""
    time.sleep(1.0)
    # aria-label, затем кнопки/ссылки с текстом
    xpaths: List[str] = [
        "//*[@aria-label='Войти' or @aria-label='войти']",
        "//button[contains(., 'Войти') or contains(., 'войти')]",
        "//a[contains(., 'Войти') or contains(., 'войти')]",
        "//*[@role='button' and (contains(., 'Войти') or contains(., 'войти'))]",
    ]
    for xp in xpaths:
        try:
            el = WebDriverWait(driver, min(timeout, 20)).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            el.click()
            return
        except (TimeoutException, Exception):
            continue
    raise YandexAuthError(
        "Не найдена кнопка «Войти» на dzen.ru. " + _safe_page_hint(driver)
    )


def _click_yandex_id_entry(driver: "WebDriver", timeout: float) -> None:
    time.sleep(0.8)
    candidates = [
        (By.XPATH, "//*[@aria-label='Войти через Яндекс ID' or @aria-label='Войти через яндекс id']"),
        (By.XPATH, "//*[contains(., 'Войти через Яндекс ID') or contains(., 'войти через яндекс id')]"),
    ]
    for by, val in candidates:
        try:
            el = WebDriverWait(driver, min(timeout, 25)).until(
                EC.element_to_be_clickable((by, val))
            )
            el.click()
            return
        except (TimeoutException, Exception):
            continue
    raise YandexAuthError(
        "Не найден элемент «Войти через Яндекс ID». " + _safe_page_hint(driver)
    )


def _if_voydite_s_id_use_pochta_and_login(
    driver: "WebDriver", login: str, short_wait: float
) -> bool:
    """Если на странице 'Войдите с ID' — жмём «Почта», вводим логин. Возвращает True если шаг выполнялся."""
    src = _lower_src(driver)
    if "войдите с id" not in src and "войдите с id" not in (driver.title or "").lower():
        return False
    for xp in (
        "//button[contains(., 'Почта') or contains(., 'почта')]",
        "//*[@role='tab' and (contains(., 'Почта') or contains(., 'почта'))]",
        "//*[contains(., 'Почта') and (self::button or self::a or self::div)]",
    ):
        if _wait_click(driver, By.XPATH, xp, 8.0):
            time.sleep(0.5)
            break
    login_selectors: List = [
        (By.CSS_SELECTOR, "input[aria-label='Логин или email']"),
        (By.CSS_SELECTOR, "input[aria-label='Логин или Email']"),
        (By.ID, "passp-field-login"),
        (By.CSS_SELECTOR, "input[name='login']"),
        (By.CSS_SELECTOR, "input[type='email']"),
    ]
    wait = WebDriverWait(driver, max(15, int(short_wait)))
    try:
        el = wait.until(lambda d: _find_first(d, login_selectors))
    except TimeoutException as e:
        raise YandexAuthError(
            "Не найдено поле логина (ожидалась вкладка Почта). " + _safe_page_hint(driver)
        ) from e
    el.clear()
    time.sleep(0.2)
    el.send_keys(login)
    time.sleep(0.2)
    el.send_keys(Keys.ENTER)
    time.sleep(1.2)
    return True


def _enter_login_and_submit(driver: "WebDriver", login: str, timeout: float) -> bool:
    login_selectors: List = [
        (By.CSS_SELECTOR, "input[aria-label='Логин или email']"),
        (By.CSS_SELECTOR, "input[aria-label='Логин или Email']"),
        (By.CSS_SELECTOR, "input[aria-label='Email or phone']"),
        (By.CSS_SELECTOR, "input[placeholder='Email or phone']"),
        (By.CSS_SELECTOR, "input[autocomplete='username']"),
        (By.ID, "passp-field-login"),
        (By.CSS_SELECTOR, "input[name='login']"),
        (By.CSS_SELECTOR, "input[name='identifier']"),
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.XPATH, "//input[contains(@name,'login')]"),
        (By.XPATH, "//input[contains(@id,'login')]"),
    ]
    wait = WebDriverWait(driver, max(20, int(timeout)))
    try:
        el = wait.until(lambda d: _find_first(d, login_selectors))
    except TimeoutException:
        return False
    try:
        el.clear()
    except Exception:
        pass
    el.send_keys(login)
    el.send_keys(Keys.ENTER)
    time.sleep(1.2)
    return True


def _enter_password_and_submit(driver: "WebDriver", password: str, timeout: float) -> None:
    pwd_selectors: List = [
        (By.ID, "passp-field-passwd"),
        (By.CSS_SELECTOR, "input#passp-field-passwd"),
        (By.NAME, "passwd"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
    ]
    wait = WebDriverWait(driver, max(20, int(timeout)))
    try:
        el = wait.until(lambda d: _find_first(d, pwd_selectors))
    except TimeoutException as e:
        raise YandexAuthError(
            "Не найдено поле пароля. " + _safe_page_hint(driver)
        ) from e
    el.clear()
    el.send_keys(password)
    time.sleep(0.2)
    sub = _find_first(
        driver,
        [
            (By.ID, "passp:sign-in"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(., 'Войти')]"),
        ],
    )
    if sub:
        sub.click()
    else:
        el.send_keys(Keys.ENTER)
    time.sleep(2.5)


def page_indicates_push_code(driver: "WebDriver") -> bool:
    t = (driver.title or "") + (driver.page_source or "")[:150000]
    tl = t.lower()
    markers = (
        "код из пуш",
        "введите код из пуш",
        "пуш-уведом",
        "push-уведом",
    )
    return any(m in tl for m in markers)


def _check_authenticated(driver: "WebDriver") -> bool:
    u = (driver.current_url or "").lower()
    if "passport.yandex.ru" in u and "session" not in u and "auth" in u:
        return False
    body = _lower_src(driver)[:100000]
    if "войдите" in body and "passp" in body:
        return False
    if page_indicates_push_code(driver):
        return False
    if _detect_captcha_block(driver):
        return False
    return "dzen.ru" in u or "yandex" in u


def dzen_entry_run_until_push_or_ok(
    driver: "WebDriver", login: str, password: str
) -> DzenFlowResult:
    """
    Открывает dzen.ru, проходит сценарий входа.
    'push' — требуется ввод кода (драйвер остаётся открытым).
    'ok' — сессия для дальнейшей навигации (пароль введен, пуш-экрана нет).
    """
    if not (login and password):
        raise YandexAuthError("Пустой логин или пароль")

    base = (getattr(settings, "DZEN_ENTRY_BASE_URL", None) or "https://dzen.ru/").strip()
    short_w = 45.0

    driver.get(base)
    time.sleep(2.0)
    if _detect_captcha_block(driver):
        raise YandexAuthError(
            "Обнаружена проверка SmartCaptcha/«не робот» на dzen.ru. "
            "Headless-режим и дата-центр IP часто блокируются. Попробуйте вручную, другой сеть или SELENIUM_HEADLESS=false (отладка)."
        )

    _click_voyti_on_dzen(driver, 25.0)
    time.sleep(1.0)
    _click_yandex_id_entry(driver, 25.0)
    time.sleep(2.0)

    if _detect_captcha_block(driver):
        raise YandexAuthError("Капча/антибот на этапе Яндекс ID. " + _safe_page_hint(driver))

    used_pochta = _if_voydite_s_id_use_pochta_and_login(driver, login, 25.0)
    if not used_pochta:
        if not _enter_login_and_submit(driver, login, 25.0):
            if page_indicates_push_code(driver):
                return "push"
            raise YandexAuthError(
                "Не найдено поле логина (в т.ч. Email or phone / passp-field-login). "
                + _safe_page_hint(driver)
            )

    if page_indicates_push_code(driver):
        return "push"

    _enter_password_and_submit(
        driver, password, float(getattr(settings, "YANDEX_PASSPORT_PASSWORD_TIMEOUT_SEC", 40))
    )
    time.sleep(2.0)

    if page_indicates_push_code(driver):
        return "push"

    if "passport.yandex.ru" in (driver.current_url or "").lower() and "auth" in (driver.current_url or ""):
        err = _find_first(
            driver,
            [(By.CSS_SELECTOR, ".passp-form-field__error"), (By.CSS_SELECTOR, "[role='alert']")],
        )
        msg = err.text.strip() if err else "Не удалось войти. Проверьте логин и пароль."
        raise YandexAuthError(msg or "Ошибка входа в Яндекс ID.")

    return "ok" if _check_authenticated(driver) or not page_indicates_push_code(driver) else "push"


def dzen_entry_submit_push_code(
    driver: "WebDriver", code: str
) -> None:
    c = (code or "").strip()
    if not c:
        raise YandexAuthError("Пустой код пуш-уведомления")

    selectors: List = [
        (By.CSS_SELECTOR, "input[autocomplete='one-time-code']"),
        (By.CSS_SELECTOR, "input[type='tel']"),
        (By.CSS_SELECTOR, "input[aria-label*='од']"),  # часть подписи
        (By.XPATH, "//input[contains(@aria-label,'од')]"),
    ]
    wait = WebDriverWait(driver, 25.0)
    el = None
    for by, v in selectors:
        try:
            el = wait.until(EC.element_to_be_clickable((by, v)))
            break
        except Exception:
            continue
    if not el:
        # fallback: один видимый input
        for inp in driver.find_elements(By.CSS_SELECTOR, "input"):
            if inp.is_displayed():
                el = inp
                break
    if not el:
        raise YandexAuthError("Поле для ввода кода не найдено. " + _safe_page_hint(driver))

    el.clear()
    el.send_keys(c)
    time.sleep(0.2)
    btn = _find_first(
        driver,
        [
            (By.XPATH, "//button[contains(., 'Продолж') or contains(., 'подтверд')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
        ],
    )
    if btn:
        try:
            btn.click()
        except Exception:
            el.send_keys(Keys.ENTER)
    else:
        el.send_keys(Keys.ENTER)
    time.sleep(3.0)
    if page_indicates_push_code(driver):
        s = _lower_src(driver)
        if "неверн" in s or "ошиб" in s:
            raise YandexAuthError("Код не принят. " + _safe_page_hint(driver))


def login_yandex_dzen_entry(driver: "WebDriver", login: str, password: str) -> None:
    """
    Полный сценарий dzen-входа без пуша (для publish/collect: если пуш — ошибка).
    """
    r = dzen_entry_run_until_push_or_ok(driver, login, password)
    if r == "push":
        raise YandexAuthError(
            "Требуется код из пуш-уведомления. Используйте проверку во вкладке «Авторизация» (двухшаговый вход) или войдите вручную."
        )


def yandex_auth_dispatch(driver: "WebDriver", login: str, password: str) -> None:
    """Точка входа для ботов: dzen-флоу или прямой Passport по config."""
    if getattr(settings, "USE_DZEN_ENTRY_AUTH", True):
        login_yandex_dzen_entry(driver, login, password)
    else:
        from .yandex_auth import login_yandex_passport

        login_yandex_passport(driver, login, password)
