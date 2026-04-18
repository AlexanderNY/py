"""Диагностика: скриншот при ошибке Selenium → S3 (ключ содержит подстроку «diag»)."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from config import settings
from storage_helper import get_storage

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


def _sanitize_label(label: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", (label or "").strip())[:100]
    return s or "step"


async def _put_png(key: str, png: bytes) -> None:
    storage = get_storage()
    if not storage:
        return
    await storage.put(key, png, content_type="image/png")


def upload_selenium_diag_screenshot(
    driver: "WebDriver",
    label: str,
    *,
    user_id: Optional[int] = None,
) -> Optional[str]:
    """
    Делает PNG-скриншот и загружает в S3. Имя объекта обязательно содержит «diag».

    Returns:
        Ключ объекта в бакете или None (S3 не настроен, сбой снимка/загрузки).
    """
    if driver is None:
        return None
    try:
        png = driver.get_screenshot_as_png()
    except Exception as e:
        logger.warning("selenium_diag: get_screenshot_as_png failed: %s", e)
        return None

    if not get_storage():
        logger.debug("selenium_diag: S3 not configured, skip upload")
        return None

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid_part = f"uid{user_id}" if user_id is not None else "nouid"
    safe = _sanitize_label(label)
    prefix = (settings.S3_DIAG_PREFIX or "dzen/diag").strip().strip("/")
    # Требование: имя файла содержит «diag»
    key = f"{prefix}/diag_selenium_{ts}_{uid_part}_{safe}.png"

    try:
        asyncio.run(_put_png(key, png))
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e).lower() or "already running" in str(
            str(e)
        ).lower():
            logger.warning(
                "selenium_diag: cannot run async S3 upload in this context (%s); skip upload", e
            )
            return None
        logger.warning("selenium_diag: S3 upload failed: %s", e)
        return None
    except Exception as e:
        logger.warning("selenium_diag: S3 upload failed: %s", e)
        return None

    bucket = getattr(settings, "S3_BUCKET", "")
    logger.info("selenium_diag: screenshot uploaded s3://%s/%s", bucket, key)
    return key


def capture_selenium_error_to_s3(
    driver: Optional["WebDriver"],
    label: str,
    *,
    user_id: Optional[int] = None,
) -> Optional[str]:
    """
    Вызывать из except-блоков при ошибке сценария Selenium (драйвер ещё открыт).
    Возвращает ключ S3 или None.
    """
    if driver is None:
        return None
    return upload_selenium_diag_screenshot(driver, label, user_id=user_id)
