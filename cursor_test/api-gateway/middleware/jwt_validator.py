import jwt
from typing import Optional
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings, PUBLIC_ENDPOINTS
from utils.exceptions import TokenValidationException


class JwtValidator:
    """Валидатор JWT токенов."""
    
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def decode_token(self, token: str) -> dict:
        """Декодирует JWT токен.
        
        Args:
            token: JWT токен
        
        Returns:
            Декодированные данные токена (payload)
        
        Raises:
            TokenValidationException: Если токен невалидный или истек
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError as error:
            raise TokenValidationException("Token has expired.") from error
        except jwt.InvalidTokenError as error:
            raise TokenValidationException("Invalid token.") from error
    
    def validate_token(self, token: str) -> bool:
        """Валидирует JWT токен.
        
        Args:
            token: JWT токен
        
        Returns:
            True если токен валидный
        
        Raises:
            TokenValidationException: Если токен невалидный
        """
        self.decode_token(token)
        return True
    
    def extract_token_from_header(self, authorization_header: Optional[str]) -> str:
        """Извлекает токен из Authorization header.
        
        Args:
            authorization_header: Значение Authorization header
        
        Returns:
            JWT токен без префикса Bearer
        
        Raises:
            TokenValidationException: Если header отсутствует или неверного формата
        """
        if not authorization_header:
            raise TokenValidationException("Authorization header is missing.")
        
        parts = authorization_header.split()
        
        if len(parts) != 2:
            raise TokenValidationException("Invalid authorization header format.")
        
        scheme, token = parts
        
        if scheme.lower() != "bearer":
            raise TokenValidationException("Invalid authentication scheme. Use Bearer.")
        
        return token
    
    def get_user_from_token(self, token: str) -> dict:
        """Получает данные пользователя из токена.
        
        Args:
            token: JWT токен
        
        Returns:
            Словарь с данными пользователя из токена
        """
        payload = self.decode_token(token)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "exp": payload.get("exp"),
        }


# Глобальный экземпляр JwtValidator
jwt_validator = JwtValidator(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM
)


# HTTP Bearer security scheme для OpenAPI документации
security_scheme = HTTPBearer(auto_error=False)


def check_public_endpoint(endpoint_path: str) -> bool:
    """Проверяет, является ли endpoint публичным (не требует JWT).
    
    Args:
        endpoint_path: Путь endpoint'а
    
    Returns:
        True если endpoint публичный
    """
    # Точное совпадение
    if endpoint_path in PUBLIC_ENDPOINTS:
        return True
    
    # Проверка префиксов для заглушек
    stub_prefixes = ["/scheduler", "/tg-bot", "/vk-bot", "/wp-bot", "/url-bot"]
    for prefix in stub_prefixes:
        if endpoint_path.startswith(prefix):
            return True
    
    return False


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[dict]:
    """Dependency для получения текущего пользователя из JWT.
    
    Для публичных endpoints возвращает None без ошибки.
    Для защищенных endpoints требует валидный JWT.
    
    Args:
        request: FastAPI Request объект
        credentials: HTTP Bearer credentials
    
    Returns:
        Данные пользователя или None для публичных endpoints
    
    Raises:
        TokenValidationException: Если JWT отсутствует или невалидный
    """
    endpoint_path = request.url.path
    
    # Публичные endpoints не требуют аутентификации
    if check_public_endpoint(endpoint_path):
        return None
    
    # Для защищенных endpoints требуем токен
    if not credentials:
        raise TokenValidationException("Authorization header is required.")
    
    return jwt_validator.get_user_from_token(credentials.credentials)


async def validate_jwt_middleware(request: Request) -> Optional[dict]:
    """Валидирует JWT из запроса (для использования в middleware).
    
    Args:
        request: FastAPI Request объект
    
    Returns:
        Данные пользователя или None для публичных endpoints
    
    Raises:
        TokenValidationException: Если JWT невалидный
    """
    endpoint_path = request.url.path
    
    # Публичные endpoints
    if check_public_endpoint(endpoint_path):
        return None
    
    authorization_header = request.headers.get("authorization")
    
    if not authorization_header:
        raise TokenValidationException("Authorization header is required.")
    
    token = jwt_validator.extract_token_from_header(authorization_header)
    return jwt_validator.get_user_from_token(token)


