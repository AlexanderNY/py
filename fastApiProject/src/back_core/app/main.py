# back_core/app/main.py

from fastapi import FastAPI, Body, Response, HTTPException
import httpx
import os
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="User Interface")

origins = [
    "http://localhost:5173/",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8001/",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

services = [[True,"auth","Сервис авторизации","172.10.10.1","8001",""],[False,"front","Сервис с Web интерфейсом","172.10.10.2","8002",""],[True,"core","Сервис синхронизации всех API","172.10.10.3","8003",""],[True,"scheduler","Сервис работы с задачами по расписанию","172.10.10.4","8004",""]]

#API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api_gateway:8002")
#AUTH_URL = os.getenv("AUTH_URL", "http://auth:8001")
#client = httpx.AsyncClient()

@app.get("/")
async def root():
    """Главная страница UI"""
    return {
        "message": "Core System Service",
        "endpoints": {
            "setup_monitoring": "POST /setup-monitoring",
            "monitoring_status": "GET /monitoring-status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user_interface"}

@app.get("/healthchecks")
async def health_checks():
    """Check each service endpoint"""
    #check JWT

    #get services

    for i in range(len(services)):
        if services[i][0] == True:
            print("проверяем", services[i][1])
            async with httpx.AsyncClient() as client:
                try:
                    # Fixed: added await and using AUTH_URL from environment
                    service_url = 'http://'+services[i][3]+':'+services[i][4]+'/health'
                    response = await client.get(
                       service_url,
                       timeout=30.0
                    )
                    services[i][5] = response.json()
                except httpx.ConnectError:
                    raise HTTPException(status_code=503, detail="Cannot connect to auth service")
                except httpx.TimeoutException:
                    raise HTTPException(status_code=504, detail="Request to auth service timed out")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        else:
            print("сервис", services[i][1], "не проверяем")
            services[i][5] = "Проверка отключена"
    #for each enabled service get healthcheck

    #return result
    return json.dumps(services)





#todo url 172.0.0.1 to ENV and take it from k8s

@app.get("/test")
async def test():
    print("test")
    data= {
        "name": "Alex",
        "pwd": "a1234567890",
        "timer": "300"
    }
    headers = {
        'user-agent': 'my-app/0.0.1',
        'Content-Type':'application/json'
    }
    #'http://172.10.10.1:8001/auth'
    async with httpx.AsyncClient() as client:
        try:
            # Fixed: added await and using AUTH_URL from environment
            response = await client.post(
                'http://172.10.10.1:8001/auth',
                json=data,
                headers=headers,
                timeout=30.0
            )
            return {
                "status_code": response.status_code,
                "response_data": response.json() if response.status_code == 200 else response.text,
                "response_headers": response.headers
            }
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to auth service")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request to auth service timed out")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

'''
from __future__ import annotations

import asyncio
from typing import Final

from aiohttp import ClientSession
from fastapi import Depends, FastAPI
from starlette.requests import Request

app: Final = FastAPI()


@app.on_event("startup")
async def startup_event():
    setattr(app.state, "client_session", ClientSession(raise_for_status=True))


@app.on_event("shutdown")
async def shutdown_event():
    await asyncio.wait((app.state.client_session.close()), timeout=5.0)


def client_session_dep(request: Request) -> ClientSession:
    return request.app.state.client_session


@app.get("/")
async def root(
    client_session: ClientSession = Depends(client_session_dep),
) -> str:
    async with client_session.get(
        "https://example.com/", raise_for_status=True
    ) as the_response:
        return await the_response.text()

'''
#todo start a session