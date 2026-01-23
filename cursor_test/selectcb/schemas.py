from pydantic import BaseModel
from typing import List


class ProductResponse(BaseModel):
    """Схема продукта."""
    product_id: int
    product_description: str


class SearchResponse(BaseModel):
    """Схема ответа для поиска заказа."""
    order_id: str
    login: str
    product_ids: List[int]


class SubmitRequest(BaseModel):
    """Схема запроса для создания заказа."""
    login: str
    product_ids: List[int]


class SubmitResponse(BaseModel):
    """Схема ответа для создания заказа."""
    message: str
    order_id: str
