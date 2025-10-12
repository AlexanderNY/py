# auth/app/main.py
from fastapi import FastAPI, Body
from pydantic import BaseModel, EmailStr
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import jwt
import time, datetime
from datetime import timedelta
from typing import Union
import bcrypt

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    access_token_expires: str

class UserDTO(BaseModel):
    id: int
    login: str
    email: str
    password: str

#todo to ENV
SECRET_KEY = "secret-key"  # Заменить на надежный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30
REFRESH_TOKEN_EXPIRE = 7


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
    ,
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
    ,
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
}

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def create_access_token(self, data:dict, expires_delta: timedelta) -> str:
    return False

def decode_token(self, token: str):
    return False

def validate_user(self, email: str, password: str) -> Union[UserDTO, bool]:
    user: UserDTO = user_repository.select_user_by_email(email)
    if user and user.password.__eq__(password):
        return user
    else:
        return False


def login_for_access_token(self, email: str, password: str) -> Token:
    user: UserDTO = self.validate_user(email, password)  # проверка введенных данных

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=15)  # время действия токена
    # данные для кодирования
    access_token = self.create_access_token(
        data={"email": user.email, "password": user.password},
        expires_delta=access_token_expires
    )  # создание токена
    return Token(access_token=access_token, token_type="bearer", access_token_expires=str(access_token_expire))

def get_current_user(self, token: str):
    # заранее подготовим исключение
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # декодировка токена
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # данные из токена
        email: str = payload.get("email")
        password: str = payload.get("password")
        exp: str = payload.get("exp")

        # если в токене нет поля email
        if email is None:
            raise credentials_exception

        # если время жизни токена истекло
        if datetime.fromtimestamp(float(exp)) - datetime.now() < timedelta(0):
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    # проверка данных
    user: UserDTO = self.validate_user(email, password)

    if user is None:
        raise credentials_exception
    return user

app = FastAPI(title="Auth Service")

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


@app.options("/auth")
async def get_auth_status_test():
    """Получить статус options , для проверки доступности при обращении из браузера с помощью fetch"""
    content = {"message": "Hello handshake"}
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "Content-Type"}
    return JSONResponse(content=content, headers=headers)
@app.post("/auth")
async def get_auth_status(name: str = Body(embed=True, min_length=3, max_length=20),
                          pwd: str = Body(embed=True,  min_length=10, max_length=20),
                          timer: int = Body(embed=True, lt=1000)):

    """Получить статус авторизации"""
    try:
        # Получаем данные из БД
        pw = b'1234567890'
        s = SECRET_KEY # salt
        h = bcrypt.hashpw(pw, s)  # Hash password
        pwd = bcrypt.hashpw(pwd, s)
        if (name == "Alex" or name == "Bob") and (pwd == h) and timer>=30:
            encoded = jwt.encode({"some": "payload"}, SECRET_KEY, algorithm=ALGORITHM)
            return {"user_name": name, "user_pwd": pwd, "user_auth": True, "user_token": encoded  }
        else:
            return {
                "user_name": name,
                "user_pwd": pwd,
                "user_auth": False
            }

    except:
        return {"message": "nothing works"}


@app.post("/signup")
async def signup():
    """Страница для регистрации"""
    return {
        "message": "Auth System",
        "endpoints": {
            "setup_monitoring": "POST /auth",
        }
    }
@app.post("/signin")
async def login(user):
    #получаем токен и возращаем клиенту
    token = user_auth.login_for_access_token(user.email, user.password)
    return token

@app.post("/me")
async def read_me(token):
    #декодируем токен и получаем обьект пользователя
    return user_auth.decode_token(token.token)


@app.post("/refresh")
async def refresh():
    """Страница для обновления токена авторизации"""
    return {
        "message": "Auth System",
        "endpoints": {
            "setup_monitoring": "POST /auth",
        }
    }


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