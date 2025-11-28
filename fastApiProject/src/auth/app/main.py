# auth/app/main.py
from fastapi import FastAPI, Body, Response
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
import json
#from pydantic import BaseModel

class Token():
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_token(self, user_data, expires_in_hours=24):
        """
        Генерация JWT токена
        """
        payload = {
            **user_data,
            'token_id': uuid.uuid4(),
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + timedelta(hours=expires_in_hours)
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token):
        """
        Проверка и декодирование JWT токена
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

    def refresh_token(self, token, expires_in_hours=24):
        """
        Обновление токена
        """
        payload = self.verify_token(token)

        # Удаляем временные метки из старого payload
        payload.pop('iat', None)
        payload.pop('exp', None)

        # Генерируем новый токен
        return self.generate_token(user_data, expires_in_hours)

#todo to ENV
SECRET_KEY = "$2b$12$xyiAcpacCfrFN3wl3ayJT."  # Заменить на надежный ключ, но по правилам gensault+a-string-secret-at-least-256-bits-long
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30
REFRESH_TOKEN_EXPIRE = 7




def get_hashed_password(password: str) -> bytes:
    password = bytes(password, 'utf-8')
    s = bytes(SECRET_KEY, 'utf-8')
    password = bcrypt.hashpw(password, s)
    return (password)






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

def get_user(name):
    # Получаем данные из БД
    pw = "a1234567890"
    pw = bytes(pw, 'utf-8')
    s = bytes(SECRET_KEY, 'utf-8') # salt
    hpwd_db = bcrypt.hashpw(pw, s)  # Hash password
    name_db = "Alex"

    return (name_db,hpwd_db)


@app.options("/auth")
async def get_auth_status_test():
    """Получить статус options , для проверки доступности при обращении из браузера с помощью fetch"""
    content = {"message": "Hello handshake"}
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "Content-Type"}
    return JSONResponse(json=content, headers=headers)
@app.post("/auth")
async def get_auth_status(name: str = Body(embed=True, min_length=3, max_length=20),
                          pwd: str = Body(embed=True,  min_length=10, max_length=20),
                          timer: int = Body(embed=True, lt=1000)):
    #SECRET_KEY="$2b$12$xyiAcpacCfrFN3wl3ayJT."
    encoded=Token(SECRET_KEY, algorithm='HS256')
    pwd = get_hashed_password(pwd)
    s = bytes(SECRET_KEY, 'utf-8')
    name_db, hpwd_db = get_user(name)
    print(name)
    print(name_db)
    print(pwd)
    print(hpwd_db)
    """Получить статус авторизации"""
    try:
        name_db,hpwd_db=get_user(name)
        print(name_db,hpwd_db)
        if (name == name_db) and (pwd == hpwd_db) and timer>=30:
            print('name=name')
            user_data = {
                'user_name': 'name',
                'user_id': '12',
                'token_id': 'q',
                'user_role': 'owner'
            }

            encoded = encoded.generate_token(user_data, expires_in_hours=48)
            print('encoded')
            #encoded = jwt.encode(payload ={"id": "123","role": "owner","data": "payload"}, key=SECRET_KEY, algorithm=ALGORITHM)
            #Response.headers["Secret-Code"] = "123459"
            content= {
                "message": "it works!",
                "user_name": name,
                #"user_pwd": pwd,
                "user_auth": True,
                "user_token":"header"
            }
            headers = {"X-My-Custom-Header": encoded}
            return JSONResponse(content=content, headers=headers)
        else:
            content = {
                "message": "Nonono",
                "user_name": name,
                #"user_pwd": pwd,
                "user_auth": False,
                "user_token": ""
            }
            headers = {"X-My-Custom-Header": "Value"}
            return JSONResponse(content=content, headers=headers)


    except:
        content = {
            "message": "nothing works",
            "user_name": name,
           # "user_pwd": pwd,
            "user_auth": False,
            "user_token": ""
        }
        headers = {"X-My-Custom-Header": "Value"}
        return JSONResponse(content=content, headers=headers)





@app.post("/signup")
async def signup():
    """Страница для регистрации"""
    return {
        "message": "Auth System",
        "endpoints": {
            "setup_monitoring": "POST /auth",
        }
    }
# @app.post("/signin")
# async def login(user):
#     #получаем токен и возращаем клиенту
#     token = user_auth.login_for_access_token(user.email, user.password)
#     return token

# @app.post("/me")
# async def read_me(token):
#     #декодируем токен и получаем обьект пользователя
#     return user_auth.decode_token(token.token)


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




# def validate_user(self, email: str, password: str) -> Union[UserDTO, bool]:
#     user: UserDTO = user_repository.select_user_by_email(email)
#     if user and user.password.__eq__(password):
#         return user
#     else:
#         return False


# def login_for_access_token(self, email: str, password: str) -> Token:
#     user: UserDTO = self.validate_user(email, password)  # проверка введенных данных
#
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     access_token_expires = timedelta(minutes=15)  # время действия токена
#     # данные для кодирования
#     access_token = self.create_access_token(
#         data={"email": user.email, "password": user.password},
#         expires_delta=access_token_expires
#     )  # создание токена
#     return Token(access_token=access_token, token_type="bearer", access_token_expires=str(access_token_expire))

# def get_current_user(self, token: str):
#     # заранее подготовим исключение
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         # декодировка токена
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#
#         # данные из токена
#         email: str = payload.get("email")
#         password: str = payload.get("password")
#         exp: str = payload.get("exp")
#
#         # если в токене нет поля email
#         if email is None:
#             raise credentials_exception
#
#         # если время жизни токена истекло
#         if datetime.fromtimestamp(float(exp)) - datetime.now() < timedelta(0):
#             raise credentials_exception
#
#     except InvalidTokenError:
#         raise credentials_exception
#
#     # проверка данных
#     user: UserDTO = self.validate_user(email, password)
#
#     if user is None:
#         raise credentials_exception
#     return user