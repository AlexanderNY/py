"""Роутер для получения статистики."""

from fastapi import APIRouter, Request
from services.statistics_service import statistics_service
from schemas import StatisticsResponse, UserStatisticsResponse
import httpx
from config import settings


router = APIRouter(tags=["Statistics"])


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Получает статистику постов по всем платформам.
    
    Returns:
        StatisticsResponse: Статистика по платформам
    """
    services = await statistics_service.get_statistics()
    return {"services": services}


@router.get("/users-statistics", response_model=UserStatisticsResponse)
async def get_users_statistics(request: Request):
    """Получает статистику использования по пользователям.
    
    Returns:
        UserStatisticsResponse: Статистика по пользователям
    """
    # Получаем статистику постов по пользователям
    posts_stats = await statistics_service.get_users_statistics()
    
    # Получаем информацию о пользователях из auth сервиса через API Gateway
    # Передаем токен из входящего запроса
    try:
        # Извлекаем токен из заголовков запроса
        authorization = request.headers.get("Authorization", "")
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        
        async with httpx.AsyncClient() as client:
            # Получаем список всех пользователей через API Gateway
            auth_url = f"{settings.API_GATEWAY_URL}/auth/users"
            response = await client.get(auth_url, headers=headers)
            response.raise_for_status()
            users_data = response.json()
    except Exception:
        # Если не удалось получить данные о пользователях, возвращаем только статистику по постам
        users_data = []
    
    # Создаем словарь пользователей для быстрого поиска
    users_dict = {user.get("id", user.get("user_id")): user for user in users_data if user.get("id") or user.get("user_id")}
    
    # Объединяем данные
    result = []
    for stat in posts_stats:
        user_id = stat["user_id"]
        user_info = users_dict.get(user_id, {})
        result.append({
            "user_id": user_id,
            "username": user_info.get("username", f"User {user_id}"),
            "email": user_info.get("email", ""),
            "role": user_info.get("role", "guest"),
            "total_posts": stat["total_posts"],
            "collected_posts": stat["collected_posts"],
            "processed_posts": stat["processed_posts"],
            "published_posts": stat["published_posts"]
        })
    
    return {"users": result}
