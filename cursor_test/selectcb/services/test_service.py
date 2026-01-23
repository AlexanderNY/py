"""Сервис для работы с заказами и продуктами."""

import uuid
from typing import List, Optional
from database import get_db_connection
from schemas import SearchResponse


class TestService:
    """Сервис для работы с тестовыми заказами."""
    
    async def get_order_data(self, order_id: str) -> Optional[SearchResponse]:
        """Получает данные заказа по order_id.
        
        Args:
            order_id: Идентификатор заказа
            
        Returns:
            SearchResponse с данными заказа или None если заказ не найден
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                # Получаем данные заказа
                await cur.execute(
                    "SELECT order_id, login FROM orders WHERE order_id = %s",
                    (order_id,)
                )
                order_row = await cur.fetchone()
                
                if not order_row:
                    return None
                
                order_id_db, login = order_row
                
                # Получаем список product_id для этого заказа
                await cur.execute(
                    "SELECT product_id FROM orderdetails WHERE order_id = %s",
                    (order_id,)
                )
                product_rows = await cur.fetchall()
                product_ids = [row[0] for row in product_rows]
                
                return SearchResponse(
                    order_id=order_id_db,
                    login=login,
                    product_ids=product_ids
                )
        finally:
            conn.close()
    
    async def get_products(self) -> List[dict]:
        """Получает список всех продуктов.
        
        Returns:
            Список словарей с product_id и product_description
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT product_id, product_description FROM products ORDER BY product_description"
                )
                rows = await cur.fetchall()
                return [
                    {"product_id": row[0], "product_description": row[1]}
                    for row in rows
                ]
        finally:
            conn.close()
    
    async def create_order(self, login: str, product_ids: List[int]) -> str:
        """Создает новый заказ с деталями.
        
        Args:
            login: Логин пользователя
            product_ids: Список идентификаторов продуктов
            
        Returns:
            Идентификатор созданного заказа
        """
        # Генерируем order_id на основе UUID
        order_id = str(uuid.uuid4())
        
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                # Начинаем транзакцию
                await cur.execute("BEGIN")
                
                try:
                    # Вставляем заказ
                    await cur.execute(
                        "INSERT INTO orders (order_id, login) VALUES (%s, %s)",
                        (order_id, login)
                    )
                    
                    # Вставляем детали заказа
                    for product_id in product_ids:
                        await cur.execute(
                            "INSERT INTO orderdetails (order_id, product_id) VALUES (%s, %s)",
                            (order_id, product_id)
                        )
                    
                    # Коммитим транзакцию
                    await cur.execute("COMMIT")
                    return order_id
                except Exception as e:
                    # Откатываем транзакцию в случае ошибки
                    await cur.execute("ROLLBACK")
                    raise e
        finally:
            conn.close()


# Singleton экземпляр сервиса
test_service = TestService()
