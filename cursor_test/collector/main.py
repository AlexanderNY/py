"""Collector: сбор постов из *_posts -> posts и распределение ready -> *_posts."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, status

from config import settings, SOURCE_TABLES, TARGET_TABLES, COLLECTOR_FUNCTIONS_FOR_ADMIN
from database import init_db, close_db, get_db_connection
from services.collect_service import collect_service
from services.distribute_service import distribute_service
from schemas import (
    HealthResponse,
    CycleResult,
    ServiceStatus,
    LoopStatus,
    MetricsResponse,
    PlatformMetric,
    CollectorFunction,
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

_collect_task: asyncio.Task | None = None
_distribute_task: asyncio.Task | None = None
_started_at: datetime | None = None


# ── Фоновые циклы ──────────────────────────────────────────────

async def _collector_loop() -> None:
    """Фоновый цикл сбора постов из *_posts -> posts."""
    while True:
        try:
            await collect_service.run_collect_cycle()
        except Exception:
            logger.exception("Error in collector loop")
        await asyncio.sleep(settings.COLLECT_INTERVAL_SEC)


async def _distributor_loop() -> None:
    """Фоновый цикл распределения ready-постов из posts -> *_posts."""
    while True:
        try:
            await distribute_service.run_distribute_cycle()
        except Exception:
            logger.exception("Error in distributor loop")
        await asyncio.sleep(settings.DISTRIBUTE_INTERVAL_SEC)


# ── Lifespan ────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _collect_task, _distribute_task, _started_at

    await init_db()
    _started_at = datetime.utcnow()
    logger.info(
        "Collector started; collect every %ds, distribute every %ds",
        settings.COLLECT_INTERVAL_SEC,
        settings.DISTRIBUTE_INTERVAL_SEC,
    )

    _collect_task = asyncio.create_task(_collector_loop())
    _distribute_task = asyncio.create_task(_distributor_loop())

    yield

    for task in (_collect_task, _distribute_task):
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    await close_db()
    logger.info("Collector stopped")


# ── FastAPI ─────────────────────────────────────────────────────

app = FastAPI(title="Collector", version="1.0.0", lifespan=lifespan)


@app.get("/", response_model=HealthResponse)
async def root():
    """Корневой endpoint."""
    return HealthResponse(status="running", service="collector")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Healthcheck."""
    return HealthResponse(status="healthy", service="collector", server_time=datetime.utcnow().isoformat() + "Z")


@app.get("/status", response_model=ServiceStatus)
async def get_status():
    """Текущий статус фоновых циклов и конфигурация."""
    return ServiceStatus(
        service="collector",
        version="1.0.0",
        collect_interval_sec=settings.COLLECT_INTERVAL_SEC,
        distribute_interval_sec=settings.DISTRIBUTE_INTERVAL_SEC,
        collect_batch_size=settings.COLLECT_BATCH_SIZE,
        distribute_batch_size=settings.DISTRIBUTE_BATCH_SIZE,
        collector=LoopStatus(
            last_run_at=collect_service.last_run_at,
            total_processed=collect_service.total_collected,
            last_cycle_count=collect_service.last_cycle_collected,
        ),
        distributor=LoopStatus(
            last_run_at=distribute_service.last_run_at,
            total_processed=distribute_service.total_distributed,
            last_cycle_count=distribute_service.last_cycle_distributed,
        ),
        current_time=datetime.utcnow().isoformat() + "Z",
        started_at=_started_at.isoformat() + "Z" if _started_at else None,
        collect_functions=[CollectorFunction(**opt) for opt in COLLECTOR_FUNCTIONS_FOR_ADMIN],
    )


@app.post("/collect/run", response_model=CycleResult)
async def force_collect():
    """Принудительный запуск одного цикла сбора."""
    try:
        count = await collect_service.run_collect_cycle()
        return CycleResult(
            status="success",
            message=f"Collect cycle completed, {count} posts collected",
            count=count,
        )
    except Exception as e:
        logger.exception("Force collect error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collect cycle failed: {e}",
        )


@app.post("/distribute/run", response_model=CycleResult)
async def force_distribute():
    """Принудительный запуск одного цикла распределения."""
    try:
        count = await distribute_service.run_distribute_cycle()
        return CycleResult(
            status="success",
            message=f"Distribute cycle completed, {count} posts distributed",
            count=count,
        )
    except Exception as e:
        logger.exception("Force distribute error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Distribute cycle failed: {e}",
        )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Метрики по количеству постов в каждой таблице по статусам."""
    platforms: list[PlatformMetric] = []

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Метрики по каждой платформенной таблице
            for source in SOURCE_TABLES:
                platform = source["platform"]
                table = source["table"]
                try:
                    await cur.execute(
                        f"""
                        SELECT
                            COALESCE(SUM(CASE WHEN status = 'collected' THEN 1 ELSE 0 END), 0),
                            COALESCE(SUM(CASE WHEN status = 'ready' THEN 1 ELSE 0 END), 0),
                            COALESCE(SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END), 0)
                        FROM {table}
                        """
                    )
                    row = await cur.fetchone()
                    platforms.append(
                        PlatformMetric(
                            platform=platform,
                            table=table,
                            collected_count=row[0],
                            ready_count=row[1],
                            processing_count=row[2],
                        )
                    )
                except Exception:
                    logger.warning("Could not get metrics for %s", table)

            # Метрики по центральной таблице posts
            await cur.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN status = 'ready' THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN status = 'distributed' THEN 1 ELSE 0 END), 0),
                    COUNT(*)
                FROM posts
                """
            )
            posts_row = await cur.fetchone()

    return MetricsResponse(
        platforms=platforms,
        posts_table={
            "processing": posts_row[0],
            "ready": posts_row[1],
            "distributed": posts_row[2],
            "total": posts_row[3],
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
