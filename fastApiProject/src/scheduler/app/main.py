# scheduler/app/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import asyncio
import httpx
import os
from typing import Dict

app = FastAPI(title="Scheduler Service")

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api_gateway:8000")


class ScheduleRequest(BaseModel):
    config_id: str
    schedule: str
    email: EmailStr


# Хранилище задач (в реальном проекте используйте БД или Redis)
scheduled_tasks: Dict[str, asyncio.Task] = {}


async def execute_monitoring_task(config_id: str, email: str):
    """Выполнение задачи мониторинга"""
    print(f"Executing monitoring task for config {config_id}")

    # Здесь будет логика выполнения мониторинга
    # Пока просто имитируем работу
    async with httpx.AsyncClient() as client:
        try:
            # Получаем конфигурацию из API Gateway
            response = await client.get(f"{API_GATEWAY_URL}/configs")
            configs = response.json()

            if config_id in configs:
                config = configs[config_id]
                print(f"Monitoring {len(config['telegram_channels'])} Telegram channels")
                print(f"Monitoring {len(config['web_resources'])} web resources")

                # Имитация работы
                await asyncio.sleep(2)
                print(f"Task completed for {email}")

        except Exception as e:
            print(f"Error executing task: {e}")


def get_interval(schedule: str) -> int:
    """Получить интервал в секундах"""
    intervals = {
        'hourly': 3600,
        'daily': 86400,
        'weekly': 604800
    }
    return intervals.get(schedule, 3600)  # default hourly


async def periodic_task(config_id: str, email: str, interval: int):
    """Периодическое выполнение задачи"""
    while True:
        await execute_monitoring_task(config_id, email)
        await asyncio.sleep(interval)


@app.post("/schedule")
async def schedule_task(request: ScheduleRequest, background_tasks: BackgroundTasks):
    """Запланировать задачу мониторинга"""
    interval = get_interval(request.schedule)

    # Создаем периодическую задачу
    task = asyncio.create_task(
        periodic_task(request.config_id, request.email, interval)
    )

    scheduled_tasks[request.config_id] = task
    print(f"Scheduled task for config {request.config_id} with interval {interval}s")

    return {"status": "scheduled", "config_id": request.config_id, "interval": interval}


@app.delete("/schedule/{config_id}")
async def cancel_schedule(config_id: str):
    """Отменить задачу"""
    if config_id in scheduled_tasks:
        scheduled_tasks[config_id].cancel()
        del scheduled_tasks[config_id]
        return {"status": "cancelled", "config_id": config_id}
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/tasks")
async def get_tasks():
    """Получить список активных задач"""
    return {
        "active_tasks": list(scheduled_tasks.keys()),
        "count": len(scheduled_tasks)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "scheduler"}