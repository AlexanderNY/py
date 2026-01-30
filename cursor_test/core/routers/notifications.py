"""Роутер для работы с уведомлениями."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from database import get_db_connection, release_db_connection
from schemas import NotificationCreate, Notification, NotificationResponse


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    """Создает новое уведомление.
    
    Требует JWT аутентификации и роли admin.
    
    Args:
        notification: Данные уведомления
        x_user_id: ID пользователя из заголовка (добавляется api-gateway)
        x_user_role: Роль пользователя из заголовка (добавляется api-gateway)
    
    Returns:
        Notification: Созданное уведомление
    """
    # Проверка аутентификации
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    
    # Проверка роли admin
    if x_user_role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create notifications")
    
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO notifications (message)
                VALUES (%s)
                RETURNING id, message, created_at
                """,
                (notification.message,)
            )
            row = await cur.fetchone()
            
            if not row:
                raise HTTPException(status_code=500, detail="Failed to create notification")
            
            return Notification(
                id=row[0],
                message=row[1],
                created_at=row[2]
            )
    finally:
        await release_db_connection(conn)


@router.get("", response_model=NotificationResponse)
async def get_notifications():
    """Получает 3 самых свежих уведомления.
    
    Не требует аутентификации - доступно всем пользователям.
    
    Returns:
        NotificationResponse: Список из 3 самых свежих уведомлений
    """
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, message, created_at
                FROM notifications
                ORDER BY created_at DESC
                LIMIT 3
                """
            )
            rows = await cur.fetchall()
            
            notifications = [
                Notification(
                    id=row[0],
                    message=row[1],
                    created_at=row[2]
                )
                for row in rows
            ]
            
            return NotificationResponse(notifications=notifications)
    finally:
        await release_db_connection(conn)


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    """Удаляет уведомление по ID.
    
    Требует JWT аутентификации и роли admin.
    
    Args:
        notification_id: ID уведомления для удаления
        x_user_id: ID пользователя из заголовка (добавляется api-gateway)
        x_user_role: Роль пользователя из заголовка (добавляется api-gateway)
    
    Returns:
        dict: Сообщение об успешном удалении
    """
    # Проверка аутентификации
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    
    # Проверка роли admin
    if x_user_role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete notifications")
    
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM notifications WHERE id = %s RETURNING id",
                (notification_id,)
            )
            row = await cur.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Notification not found")
            
            return {"message": "Notification deleted successfully", "id": notification_id}
    finally:
        await release_db_connection(conn)
