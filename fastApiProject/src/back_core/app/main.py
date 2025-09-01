# user_interface/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import httpx
import os

app = FastAPI(title="User Interface")

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api_gateway:8000")


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
    schedule: str


@app.post("/setup-monitoring")
async def setup_monitoring(config: MonitoringConfig):
    """Настройка мониторинга через UI"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_GATEWAY_URL}/configure",
                json=config.dict()
            )
            response.raise_for_status()
            result = response.json()

            return {
                "message": "Monitoring configured successfully",
                "config_id": result["config_id"],
                "status": result["status"]
            }

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"API Gateway unavailable: {str(e)}"
            )


@app.get("/monitoring-status")
async def get_monitoring_status():
    """Получить статус мониторинга"""
    async with httpx.AsyncClient() as client:
        try:
            # Получаем конфигурации из API Gateway
            configs_response = await client.get(f"{API_GATEWAY_URL}/configs")
            configs = configs_response.json()

            return {
                "active_configs": len(configs),
                "configurations": configs
            }

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"API Gateway unavailable: {str(e)}"
            )


@app.get("/")
async def root():
    """Главная страница UI"""
    return {
        "message": "Monitoring System User Interface",
        "endpoints": {
            "setup_monitoring": "POST /setup-monitoring",
            "monitoring_status": "GET /monitoring-status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user_interface"}