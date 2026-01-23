"""Роутер для тестовых операций с заказами."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from services.test_service import test_service
from schemas import SearchResponse, SubmitRequest, SubmitResponse, ProductResponse


router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/search/{order_id}", response_model=SearchResponse)
async def search_order(order_id: str):
    """Получает данные заказа по order_id.
    
    Args:
        order_id: Идентификатор заказа
        
    Returns:
        SearchResponse с данными заказа
        
    Raises:
        HTTPException: Если заказ не найден
    """
    order_data = await test_service.get_order_data(order_id)
    
    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order_data


@router.get("/products", response_model=List[ProductResponse])
async def get_products():
    """Получает список всех продуктов.
    
    Returns:
        Список продуктов
    """
    products = await test_service.get_products()
    return [ProductResponse(**p) for p in products]


@router.post("/submit", response_model=SubmitResponse)
async def submit_order(data: SubmitRequest):
    """Создает новый заказ с указанными продуктами.
    
    Args:
        data: Данные заказа (login и product_ids)
        
    Returns:
        SubmitResponse с сообщением и order_id
    """
    if not data.product_ids:
        raise HTTPException(status_code=400, detail="At least one product must be selected")
    
    try:
        order_id = await test_service.create_order(data.login, data.product_ids)
        return SubmitResponse(
            message="Order created successfully",
            order_id=order_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
