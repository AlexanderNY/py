"""Сервис для админ-эндпоинтов: статус сервисов и обзор таблиц постов."""

import httpx
from typing import Any, Dict, List, Optional
from datetime import datetime

from config import settings
from services.healthcheck_service import healthcheck_service


class AdminService:
    """Агрегирует данные от collector, processor, scheduler и healthcheck."""

    async def get_services_status(self) -> Dict[str, Any]:
        """Собирает healthcheck всех сервисов и детальный статус collector, processor, scheduler."""
        healthchecks = await healthcheck_service.check_all_services()

        collector_status: Optional[Dict[str, Any]] = None
        processor_status: Optional[Dict[str, Any]] = None
        scheduler_status: Optional[Dict[str, Any]] = None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.COLLECTOR_SERVICE_URL}/status")
                if resp.status_code == 200:
                    data = resp.json()
                    collector_status = {
                        "service": data.get("service", "collector"),
                        "version": data.get("version", "1.0.0"),
                        "collect_interval_sec": data.get("collect_interval_sec"),
                        "distribute_interval_sec": data.get("distribute_interval_sec"),
                        "collector": _parse_loop_status(data.get("collector")),
                        "distributor": _parse_loop_status(data.get("distributor")),
                        "error": None,
                    }
                else:
                    collector_status = {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            collector_status = {"error": str(e)}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.PROCESSOR_SERVICE_URL}/status")
                if resp.status_code == 200:
                    data = resp.json()
                    processor_status = {
                        "service": data.get("service", "processor"),
                        "version": data.get("version", "1.0.0"),
                        "process_interval_sec": data.get("process_interval_sec"),
                        "processor": _parse_loop_status(data.get("processor")),
                        "error": None,
                    }
                else:
                    processor_status = {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            processor_status = {"error": str(e)}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.SCHEDULER_SERVICE_URL}/status")
                if resp.status_code == 200:
                    data = resp.json()
                    scheduler_status = {
                        "service": data.get("service", "scheduler"),
                        "version": data.get("version", "1.0.0"),
                        "poll_interval_sec": data.get("poll_interval_sec"),
                        "last_poll_at": data.get("last_poll_at"),
                        "error": None,
                    }
                else:
                    scheduler_status = {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            scheduler_status = {"error": str(e)}

        return {
            "healthchecks": [
                {"service_name": h["service_name"], "status": h["status"], "error": h.get("error")}
                for h in healthchecks
            ],
            "collector": collector_status,
            "processor": processor_status,
            "scheduler": scheduler_status,
        }

    async def get_posts_tables_overview(self) -> Dict[str, Any]:
        """Собирает метрики таблиц постов из collector и processor."""
        platforms: List[Dict[str, Any]] = []
        posts_table_collector: Optional[Dict[str, int]] = None
        posts_table_processor: Optional[Dict[str, int]] = None
        collector_error: Optional[str] = None
        processor_error: Optional[str] = None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.COLLECTOR_SERVICE_URL}/metrics")
                if resp.status_code == 200:
                    data = resp.json()
                    for p in data.get("platforms") or []:
                        platforms.append({
                            "platform": p.get("platform", ""),
                            "table": p.get("table", ""),
                            "collected_count": p.get("collected_count", 0),
                            "ready_count": p.get("ready_count", 0),
                            "processing_count": p.get("processing_count", 0),
                        })
                    pt = data.get("posts_table")
                    if isinstance(pt, dict):
                        posts_table_collector = {k: int(v) for k, v in pt.items() if isinstance(v, (int, float))}
                else:
                    collector_error = f"HTTP {resp.status_code}"
        except Exception as e:
            collector_error = str(e)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.PROCESSOR_SERVICE_URL}/metrics")
                if resp.status_code == 200:
                    data = resp.json()
                    pt = data.get("posts_table")
                    if isinstance(pt, dict):
                        posts_table_processor = {k: int(v) for k, v in pt.items() if isinstance(v, (int, float))}
                else:
                    processor_error = f"HTTP {resp.status_code}"
        except Exception as e:
            processor_error = str(e)

        return {
            "platforms": platforms,
            "posts_table_collector": posts_table_collector,
            "posts_table_processor": posts_table_processor,
            "collector_error": collector_error,
            "processor_error": processor_error,
        }


def _parse_loop_status(raw: Any) -> Optional[Dict[str, Any]]:
    """Преобразует ответ LoopStatus от collector/processor в словарь."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        last_run = raw.get("last_run_at")
        if isinstance(last_run, str):
            try:
                last_run = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            except Exception:
                pass
        return {
            "last_run_at": last_run,
            "total_processed": int(raw.get("total_processed", 0)),
            "last_cycle_count": int(raw.get("last_cycle_count", 0)),
        }
    return None


admin_service = AdminService()
