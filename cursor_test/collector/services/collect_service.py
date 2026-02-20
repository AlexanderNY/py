"""Фаза 1: Сбор постов из платформенных таблиц (*_posts) в центральную таблицу posts."""

import json
import logging
from datetime import datetime
from typing import Any

from database import get_db_connection
from config import settings, SOURCE_TABLES

logger = logging.getLogger(__name__)

# Колонки, общие для всех *_posts и posts (без id, created_at, updated_at)
_POST_COLUMNS = [
    "user_id", "domain", "url", "title", "author", "avatar",
    "post_date", "post_text", "screenshot", "images", "image_over_text",
    "comments", "reposts", "likes", "views", "is_ad", "status",
    "post_type", "to_tg", "to_tw", "to_wp", "to_vk",
]


class CollectService:
    """Сервис сбора постов из *_posts -> posts."""

    def __init__(self) -> None:
        self.last_run_at: datetime | None = None
        self.total_collected: int = 0
        self.last_cycle_collected: int = 0

    async def run_collect_cycle(self) -> int:
        """Выполняет один цикл сбора.

        Для каждой таблицы из SOURCE_TABLES:
        1. SELECT ... WHERE status = 'collected' FOR UPDATE SKIP LOCKED
        2. INSERT INTO posts с source_platform / source_id
        3. UPDATE source status -> 'processing'

        Returns:
            Количество собранных постов за цикл.
        """
        cycle_count = 0

        for source in SOURCE_TABLES:
            platform = source["platform"]
            table = source["table"]
            try:
                count = await self._collect_from_table(platform, table)
                cycle_count += count
                if count > 0:
                    logger.info(
                        "Collected %d posts from %s", count, table
                    )
            except Exception:
                logger.exception("Error collecting from %s", table)

        self.last_run_at = datetime.utcnow()
        self.last_cycle_collected = cycle_count
        self.total_collected += cycle_count

        if cycle_count > 0:
            logger.info("Collect cycle done: %d posts total", cycle_count)

        return cycle_count

    async def _collect_from_table(self, platform: str, table: str) -> int:
        """Собирает посты из одной платформенной таблицы.

        Работает внутри одной транзакции для атомарности.
        """
        batch_size = settings.COLLECT_BATCH_SIZE
        collected_ids: list[int] = []

        async with get_db_connection() as conn:
            cur = await conn.cursor()
            try:
                await cur.execute("BEGIN")

                # 1. Выбрать посты со статусом 'collected'
                await cur.execute(
                    f"""
                    SELECT id, {", ".join(_POST_COLUMNS)}
                    FROM {table}
                    WHERE status = 'collected'
                    ORDER BY created_at
                    LIMIT %s
                    FOR UPDATE SKIP LOCKED
                    """,
                    (batch_size,),
                )
                rows = await cur.fetchall()

                if not rows:
                    await cur.execute("COMMIT")
                    return 0

                # Получаем описание колонок
                col_names = ["id"] + list(_POST_COLUMNS)

                for row in rows:
                    record = dict(zip(col_names, row))
                    source_id = record["id"]
                    collected_ids.append(source_id)

                    # 2. Вставить в posts с source_platform / source_id
                    insert_cols = list(_POST_COLUMNS) + [
                        "source_platform",
                        "source_id",
                    ]
                    placeholders = ", ".join(["%s"] * len(insert_cols))
                    col_str = ", ".join(insert_cols)

                    # Подготовка значений
                    values = [record[c] for c in _POST_COLUMNS]
                    values.append(platform)  # source_platform
                    values.append(source_id)  # source_id

                    # Статус в posts — 'collected' (далее processor переведёт в 'processing')
                    status_idx = _POST_COLUMNS.index("status")
                    values[status_idx] = "collected"

                    await cur.execute(
                        f"""
                        INSERT INTO posts ({col_str})
                        VALUES ({placeholders})
                        ON CONFLICT (source_platform, source_id)
                            WHERE source_platform IS NOT NULL
                        DO NOTHING
                        """,
                        values,
                    )

                # 3. Обновить статус в исходной таблице
                if collected_ids:
                    ids_placeholder = ", ".join(["%s"] * len(collected_ids))
                    await cur.execute(
                        f"""
                        UPDATE {table}
                        SET status = 'processing', updated_at = CURRENT_TIMESTAMP
                        WHERE id IN ({ids_placeholder})
                        """,
                        collected_ids,
                    )

                await cur.execute("COMMIT")
                return len(collected_ids)

            except Exception:
                await cur.execute("ROLLBACK")
                raise
            finally:
                cur.close()


collect_service = CollectService()
