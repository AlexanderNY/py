# auth/app/main.py
from fastapi import FastAPI, Body
from pydantic import BaseModel, EmailStr
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder




app = FastAPI(title="Auth Service")

origins = [
    "http://localhost:5173/",
    "http://localhost",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)


@app.options("/auth")
async def get_auth_status_test():
    """Получить статус options , для проверки доступности при обращении из браузера с помощью fetch"""
    content = {"message": "Hello World"}
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, PUT", "Access-Control-Allow-Headers": "Content-Type"}
    return JSONResponse(content=content, headers=headers)
@app.post("/auth")
async def get_auth_status(name: str = Body(embed=True, min_length=3, max_length=20),
                          pwd: str = Body(embed=True,  min_length=10, max_length=20),
                          timer: int = Body(embed=True, lt=1000)):
    """Получить статус авторизации"""
    try:
        # Получаем данные из БД
        asyncio.sleep(5)
        if (name == "Alex" or name == "Bob") and (pwd == "1234567890" or pwd == "1234567890123") and timer>=30:
            return {"user_name": name, "user_pwd": pwd, "user_auth": True }
        else:
            return {
                "user_name": name,
                "user_pwd": pwd,
                "user_auth": False
            }
    except:
        print("An error occurred:")


@app.get("/")
async def root():
    """Главная страница AUTH"""
    return {
        "message": "Auth System",
        "endpoints": {
            "setup_monitoring": "POST /auth",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user_auth"}