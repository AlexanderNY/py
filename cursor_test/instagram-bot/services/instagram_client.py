"""Обёртка над instagrapi для вызова в executor (синхронный API)."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _run_sync(coro_or_func, *args, **kwargs):
    """Запускает синхронную функцию в потоке."""
    import asyncio
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, lambda: coro_or_func(*args, **kwargs) if not asyncio.iscoroutine(coro_or_func) else None)


def _login_sync(username: str, password: str, verification_code: Optional[str] = None) -> Any:
    """Синхронный логин в Instagram через instagrapi."""
    from instagrapi import Client
    cl = Client()
    if verification_code:
        cl.login(username, password, verification_code=verification_code)
    else:
        cl.login(username, password)
    return cl


def _user_id_from_username_sync(cl: Any, username: str) -> Optional[int]:
    """Синхронно получает user_id по username."""
    try:
        return cl.user_id_from_username(username.strip())
    except Exception as e:
        logger.debug("user_id_from_username %s: %s", username, e)
        return None


def _user_medias_sync(cl: Any, user_id: int, amount: int = 20) -> List[Dict[str, Any]]:
    """Синхронно получает медиа пользователя. Возвращает список словарей."""
    try:
        medias = cl.user_medias(user_id, amount)
        result = []
        for m in medias:
            cap = getattr(m, "caption", None)
            caption = (cap.get("text", "") if isinstance(cap, dict) else cap) or ""
            images = []
            if getattr(m, "resources", None):
                for r in m.resources:
                    url = getattr(r, "thumbnail_url", None) or getattr(r, "video_url", None)
                    if url:
                        images.append(url)
            if not images and getattr(m, "thumbnail_url", None):
                images.append(m.thumbnail_url)
            if not images and getattr(m, "image_versions2", None):
                cands = m.image_versions2.get("candidates", []) if isinstance(m.image_versions2, dict) else []
                if cands and isinstance(cands[0], dict) and cands[0].get("url"):
                    images.append(cands[0]["url"])
            result.append({
                "pk": str(getattr(m, "pk", None) or getattr(m, "id", None) or ""),
                "caption": caption[:2200] if caption else "",
                "taken_at": getattr(m, "taken_at", None),
                "like_count": getattr(m, "like_count", 0) or 0,
                "comment_count": getattr(m, "comment_count", 0) or 0,
                "images": images,
            })
        return result
    except Exception as e:
        logger.warning("user_medias %s: %s", user_id, e)
        return []


def _photo_upload_sync(cl: Any, path: str, caption: str = "") -> Optional[str]:
    """Синхронно загружает фото. Возвращает media_id или code."""
    try:
        return cl.photo_upload(path, caption=caption or "")
    except Exception as e:
        logger.warning("photo_upload %s: %s", path[:80], e)
        return None


def _album_upload_sync(cl: Any, paths: List[str], caption: str = "") -> Optional[str]:
    """Синхронно загружает альбом (карусель). paths — список путей к файлам."""
    try:
        return cl.album_upload(paths, caption=caption or "")
    except Exception as e:
        logger.warning("album_upload: %s", e)
        return None


class InstagramClient:
    """Асинхронная обёртка над instagrapi Client."""

    def __init__(self, username: str, password: str, verification_code: Optional[str] = None):
        self._username = username
        self._password = password
        self._verification_code = verification_code
        self._client: Any = None

    async def login(self) -> bool:
        """Выполняет логин. Возвращает True при успехе."""
        try:
            self._client = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: _login_sync(
                    self._username,
                    self._password,
                    self._verification_code,
                ),
            )
            return self._client is not None
        except Exception as e:
            logger.error("Instagram login failed: %s", e, exc_info=True)
            return False

    async def user_id_from_username(self, username: str) -> Optional[int]:
        """Получает user_id по username."""
        if not self._client:
            if not await self.login():
                return None
        return await asyncio.get_event_loop().run_in_executor(
            None,
            _user_id_from_username_sync,
            self._client,
            username,
        )

    async def user_medias(self, user_id: int, amount: int = 20) -> List[Dict[str, Any]]:
        """Получает медиа пользователя."""
        if not self._client:
            if not await self.login():
                return []
        return await asyncio.get_event_loop().run_in_executor(
            None,
            _user_medias_sync,
            self._client,
            user_id,
            amount,
        )

    async def get_self_user_id(self) -> Optional[int]:
        """ID текущего пользователя после логина."""
        if not self._client:
            if not await self.login():
                return None
        return getattr(self._client, "user_id", None)

    async def photo_upload(self, path: str, caption: str = "") -> Optional[str]:
        """Загружает одно фото. Возвращает media_id/code или None."""
        if not self._client:
            if not await self.login():
                return None
        return await asyncio.get_event_loop().run_in_executor(
            None,
            _photo_upload_sync,
            self._client,
            path,
            caption,
        )

    async def album_upload(self, paths: List[str], caption: str = "") -> Optional[str]:
        """Загружает альбом (карусель)."""
        if not self._client:
            if not await self.login():
                return None
        return await asyncio.get_event_loop().run_in_executor(
            None,
            _album_upload_sync,
            self._client,
            paths,
            caption,
        )
