from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db, close_db
from routers import profile, auth, security


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчики событий жизненного цикла приложения."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Auth Service",
    description="Микросервис авторизации и аутентификации",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(security.router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Auth Service API"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return { 
        "status": "healthy", 
        "service": "auth" 
    }


