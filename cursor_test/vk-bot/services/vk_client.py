"""Обёртка над vk_api для вызова в executor (синхронный API)."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import vk_api

logger = logging.getLogger(__name__)


def _wall_get_sync(access_token: str, owner_id: int, count: int = 20) -> Dict[str, Any]:
    """Синхронный вызов wall.get. owner_id для группы отрицательный (например -123456)."""
    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()
    return vk.wall.get(owner_id=owner_id, count=count, filter="owner")


def _wall_post_sync(
    access_token: str,
    owner_id: int,
    message: str,
    from_group: bool = True,
    attachments: Optional[str] = None,
) -> Dict[str, Any]:
    """Синхронный вызов wall.post. owner_id — ID группы (отрицательный)."""
    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()
    params = {
        "owner_id": owner_id,
        "message": message[:16384] if message else "",
        "from_group": 1 if from_group else 0,
    }
    if attachments:
        params["attachments"] = attachments
    return vk.wall.post(**params)


class VkClient:
    """Клиент VK API. Вызовы выполняются в executor, чтобы не блокировать event loop."""

    def __init__(self, access_token: str):
        self._access_token = access_token

    async def wall_get(self, owner_id: int, count: int = 20) -> List[Dict[str, Any]]:
        """Получает посты со стены. owner_id для группы — отрицательное число."""
        try:
            result = await asyncio.to_thread(
                _wall_get_sync, self._access_token, owner_id, count
            )
            return result.get("items") or []
        except Exception as e:
            logger.error("wall.get owner_id=%s error: %s", owner_id, e, exc_info=True)
            return []

    async def wall_post(
        self,
        owner_id: int,
        message: str,
        from_group: bool = True,
        attachments: Optional[str] = None,
    ) -> Optional[int]:
        """Публикует пост на стену. Возвращает post_id при успехе."""
        try:
            result = await asyncio.to_thread(
                _wall_post_sync,
                self._access_token,
                owner_id,
                message,
                from_group,
                attachments,
            )
            return result.get("post_id")
        except Exception as e:
            logger.error("wall.post owner_id=%s error: %s", owner_id, e, exc_info=True)
            return None
