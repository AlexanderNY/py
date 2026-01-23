from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db, close_db
from routers import test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчики событий жизненного цикла приложения."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="SelectCB Service",
    description="Микросервис для работы с заказами и продуктами",
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
app.include_router(test_router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "service": "SelectCB Service API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {
        "status": "healthy",
        "service": "selectcb"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=True
    )
