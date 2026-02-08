"""Сервис скрапинга: переход по URL, извлечение по XPath, скриншот элемента."""

import logging
import os
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import settings

logger = logging.getLogger(__name__)


def _create_driver() -> webdriver.Chrome:
    """Создаёт headless Chrome/Chromium driver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    if chromedriver_path and os.path.isfile(chromedriver_path):
        service = Service(chromedriver_path)
    else:
        service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_url(url: str, xpath: str, take_screenshot: bool) -> dict[str, Any]:
    """
    Открывает URL, находит элемент по XPath, извлекает текст и опционально скриншот элемента.

    Args:
        url: URL страницы
        xpath: XPath селектор элемента
        take_screenshot: делать скриншот элемента

    Returns:
        {"text": str | None, "screenshot_base64": str | None, "error": str | None}
    """
    result: dict[str, Any] = {"text": None, "screenshot_base64": None, "error": None}
    driver = None
    try:
        driver = _create_driver()
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT_SECONDS)
        driver.get(url)
        wait = WebDriverWait(driver, settings.ELEMENT_WAIT_TIMEOUT_SECONDS)
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        result["text"] = element.text or ""
        if take_screenshot:
            result["screenshot_base64"] = element.screenshot_as_base64
    except Exception as e:
        logger.exception("Scraping failed: %s", e)
        result["error"] = str(e)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning("Driver quit: %s", e)
    return result


class ScrapingService:
    """Сервис скрапинга (фасад для совместимости)."""

    def scrape(self, url: str, xpath: str, take_screenshot: bool = False) -> dict[str, Any]:
        return scrape_url(url, xpath, take_screenshot)


scraping_service = ScrapingService()
