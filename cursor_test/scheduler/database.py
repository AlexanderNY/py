"""Подключение к БД Scheduler."""

from typing import Optional

import aiopg

from config import settings
from models import ALL_TABLES

_pool: Optional[aiopg.Pool] = None


async def init_db() -> None:
    global _pool
    if _pool is not None:
        return
    _pool = await aiopg.create_pool(
        settings.DATABASE_URL,
        minsize=1,
        maxsize=10,
    )
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            for sql in ALL_TABLES:
                await cur.execute(sql)


async def get_db_connection() -> aiopg.Connection:
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return await _pool.acquire()


async def close_db() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
