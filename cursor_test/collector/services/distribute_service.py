"""Фаза 2: Распределение обработанных постов из posts обратно в платформенные таблицы."""

import json
import logging
from datetime import datetime
from typing import Any

from database import get_db_connection
from config import settings, TARGET_TABLES

logger = logging.getLogger(__name__)

# Колонки для вставки в целевую *_posts таблицу
_POST_COLUMNS = [
    "user_id", "domain", "url", "title", "author", "avatar",
    "post_date", "post_text", "screenshot", "images", "image_over_text",
    "comments", "reposts", "likes", "views", "is_ad", "status",
    "post_type", "to_tg", "to_tw", "to_wp", "to_vk",
]

# Все флаги to_* для проверки
_TARGET_FLAGS = list(TARGET_TABLES.keys())


class DistributeService:
    """Сервис распределения постов из posts -> *_posts."""

    def __init__(self) -> None:
        self.last_run_at: datetime | None = None
        self.total_distributed: int = 0
        self.last_cycle_distributed: int = 0

    async def run_distribute_cycle(self) -> int:
        """Выполняет один цикл распределения.

        1. SELECT из posts WHERE status = 'ready' FOR UPDATE SKIP LOCKED
        2. Для каждого поста проверить флаги to_tg, to_wp, ...
        3. INSERT в целевые *_posts таблицы со статусом 'ready'
        4. UPDATE posts SET status = 'distributed'

        Returns:
            Количество распределённых постов за цикл.
        """
        batch_size = settings.DISTRIBUTE_BATCH_SIZE

        async with get_db_connection() as conn:
            cur = await conn.cursor()
            try:
                await cur.execute("BEGIN")

                # 1. Выбрать готовые посты
                select_cols = (
                    ["id", "source_platform", "source_id"] + _POST_COLUMNS
                )
                col_str = ", ".join(select_cols)

                await cur.execute(
                    f"""
                    SELECT {col_str}
                    FROM posts
                    WHERE status = 'ready'
                    ORDER BY created_at
                    LIMIT %s
                    FOR UPDATE SKIP LOCKED
                    """,
                    (batch_size,),
                )
                rows = await cur.fetchall()

                if not rows:
                    await cur.execute("COMMIT")
                    self.last_run_at = datetime.utcnow()
                    self.last_cycle_distributed = 0
                    return 0

                distributed_ids: list[int] = []

                for row in rows:
                    record = dict(zip(select_cols, row))
                    post_id = record["id"]
                    source_platform = record.get("source_platform")

                    distributed_ids.append(post_id)

                    # 2. Проверить каждый целевой флаг
                    for flag, target_info in TARGET_TABLES.items():
                        target_platform = target_info["platform"]
                        target_table = target_info["table"]

                        # Пропустить, если флаг не установлен
                        if not record.get(flag):
                            continue

                        # Пропустить, если целевая платформа = исходная
                        # (пост пришёл из tg_posts, не надо класть обратно в tg_posts)
                        if target_platform == source_platform:
                            continue

                        # 3. Вставить в целевую таблицу
                        await self._insert_into_target(
                            cur, target_table, record
                        )

                # 4. Обновить статус в posts
                if distributed_ids:
                    ids_placeholder = ", ".join(
                        ["%s"] * len(distributed_ids)
                    )
                    await cur.execute(
                        f"""
                        UPDATE posts
                        SET status = 'distributed', updated_at = CURRENT_TIMESTAMP
                        WHERE id IN ({ids_placeholder})
                        """,
                        distributed_ids,
                    )

                await cur.execute("COMMIT")

                count = len(distributed_ids)
                self.last_run_at = datetime.utcnow()
                self.last_cycle_distributed = count
                self.total_distributed += count

                if count > 0:
                    logger.info("Distribute cycle done: %d posts", count)

                return count

            except Exception:
                await cur.execute("ROLLBACK")
                raise
            finally:
                cur.close()

    async def _insert_into_target(
        self,
        cur: Any,
        target_table: str,
        record: dict[str, Any],
    ) -> None:
        """Вставляет пост в целевую платформенную таблицу со статусом 'ready'."""
        insert_cols = list(_POST_COLUMNS)
        placeholders = ", ".join(["%s"] * len(insert_cols))
        col_str = ", ".join(insert_cols)

        values = [record.get(c) for c in _POST_COLUMNS]

        # Статус в целевой таблице — 'ready' (для бота-публикатора)
        status_idx = _POST_COLUMNS.index("status")
        values[status_idx] = "ready"

        await cur.execute(
            f"""
            INSERT INTO {target_table} ({col_str})
            VALUES ({placeholders})
            """,
            values,
        )


distribute_service = DistributeService()
