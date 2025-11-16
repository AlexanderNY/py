# back_core/app/main.py

from fastapi import FastAPI, Body, Response, HTTPException

import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import jwt
import time, datetime
from datetime import timedelta
from typing import Union, List
import bcrypt

#from pydantic import BaseModel


import httpx
import os

app = FastAPI(title="User Interface")

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api_gateway:8002")
AUTH_URL = os.getenv("AUTH_URL", "http://auth:8002")

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