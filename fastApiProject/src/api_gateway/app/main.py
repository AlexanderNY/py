# api_gateway/app/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import httpx
import os

app = FastAPI(title="API Gateway")

SCHEDULER_URL = os.getenv("SCHEDULER_URL", "http://scheduler:8001")


class TelegramChannel(BaseModel):
    name: str
    url: str


class WebResource(BaseModel):
    url: str
    selectors: List[str]


class MonitoringConfig(BaseModel):
    email: EmailStr
    telegram_channels: List[TelegramChannel]
    web_resources: List[WebResource]
    schedule: str  # 'daily', 'hourly', 'weekly'


# In-memory storage (в реальном проекте используйте БД)
configs = {}


@app.post("/configure")
async def configure_monitoring(config: MonitoringConfig, background_tasks: BackgroundTasks):
    """Сохранить конфигурацию мониторинга"""
    config_id = f"config_{len(configs) + 1}"
    configs[config_id] = config.dict()

    # Отправляем задачу в scheduler
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SCHEDULER_URL}/schedule",
                json={
                    "config_id": config_id,
                    "schedule": config.schedule,
                    "email": config.email
                }
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Scheduler unavailable: {str(e)}")

    return {"status": "configured", "config_id": config_id}


@app.get("/configs")
async def get_configs():
    """Получить все конфигурации"""
    return configs


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api_gateway"}