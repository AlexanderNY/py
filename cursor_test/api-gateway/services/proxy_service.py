import httpx
from fastapi import Request, Response
from typing import Optional

from utils.exceptions import ServiceUnavailableException, BadGatewayException


class ProxyService:
    """Сервис проксирования HTTP запросов к downstream сервисам."""
    
    # Headers которые не нужно пробрасывать
    EXCLUDED_HEADERS: set[str] = {
        "host",
        "content-length",
        "transfer-encoding",
        "connection",
    }
    
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
    
    async def forward_request(
        self,
        target_url: str,
        method: str,
        request: Request,
        override_method: Optional[str] = None
    ) -> Response:
        """Перенаправляет запрос на целевой сервис.
        
        Args:
            target_url: Полный URL целевого сервиса
            method: HTTP метод исходного запроса
            request: FastAPI Request объект
            override_method: Переопределить HTTP метод (например POST -> PUT)
        
        Returns:
            FastAPI Response с данными от целевого сервиса
        """
        actual_method = override_method or method
        request_headers = self.prepare_headers(dict(request.headers))
        request_body = await request.body()
        query_params = dict(request.query_params)
        
        try:
            response = await self.http_client.request(
                method=actual_method,
                url=target_url,
                headers=request_headers,
                content=request_body if request_body else None,
                params=query_params if query_params else None,
                timeout=30.0
            )
            
            # Подготовка headers для ответа
            response_headers = self.prepare_response_headers(dict(response.headers))
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )
            
        except httpx.ConnectError as error:
            raise ServiceUnavailableException(
                service_name=self.extract_service_name(target_url)
            ) from error
        except httpx.TimeoutException as error:
            raise ServiceUnavailableException(
                service_name=self.extract_service_name(target_url)
            ) from error
        except httpx.HTTPError as error:
            raise BadGatewayException(
                message=f"Error communicating with upstream service: {str(error)}"
            ) from error
    
    def build_target_url(self, base_url: str, path: str) -> str:
        """Собирает полный URL для целевого сервиса.
        
        Args:
            base_url: Базовый URL сервиса (например http://localhost:8001)
            path: Путь на целевом сервисе (например /register)
        
        Returns:
            Полный URL
        """
        base_url = base_url.rstrip("/")
        path = path if path.startswith("/") else f"/{path}"
        return f"{base_url}{path}"
    
    def prepare_headers(self, original_headers: dict) -> dict:
        """Подготавливает headers для проксирования.
        
        Удаляет hop-by-hop headers и headers которые нельзя пробрасывать.
        
        Args:
            original_headers: Оригинальные headers из запроса
        
        Returns:
            Очищенные headers
        """
        return {
            key: value
            for key, value in original_headers.items()
            if key.lower() not in self.EXCLUDED_HEADERS
        }
    
    def prepare_response_headers(self, response_headers: dict) -> dict:
        """Подготавливает headers для ответа клиенту.
        
        Args:
            response_headers: Headers от upstream сервиса
        
        Returns:
            Очищенные headers для ответа
        """
        excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
        return {
            key: value
            for key, value in response_headers.items()
            if key.lower() not in excluded
        }
    
    def extract_service_name(self, url: str) -> str:
        """Извлекает имя сервиса из URL для логирования.
        
        Args:
            url: URL сервиса
        
        Returns:
            Имя сервиса (хост:порт)
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return f"{parsed.hostname}:{parsed.port}"
        except Exception:
            return "unknown"


# Глобальный экземпляр ProxyService
_proxy_service: Optional[ProxyService] = None


def initialize_proxy_service(http_client: httpx.AsyncClient) -> None:
    """Инициализирует глобальный ProxyService.
    
    Args:
        http_client: httpx AsyncClient для HTTP запросов
    """
    global _proxy_service
    _proxy_service = ProxyService(http_client)


def get_proxy_service() -> ProxyService:
    """Получает экземпляр ProxyService.
    
    Returns:
        Инициализированный ProxyService
    
    Raises:
        RuntimeError: Если ProxyService не инициализирован
    """
    if _proxy_service is None:
        raise RuntimeError("ProxyService not initialized. Call initialize_proxy_service() first.")
    return _proxy_service


