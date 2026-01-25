from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal


class UserRegister(BaseModel):
    """Схема для регистрации пользователя."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Схема для входа пользователя."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с токенами."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Схема запроса на обновление токена."""
    refresh_token: str


class UserProfile(BaseModel):
    """Схема профиля пользователя."""
    id: Optional[int] = None
    username: str
    email: EmailStr
    role: Literal["guest", "user", "admin"]
    is_email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Схема для обновления профиля пользователя."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class PasswordResetRequest(BaseModel):
    """Схема запроса на сброс пароля."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Схема подтверждения сброса пароля."""
    token: str
    new_password: str = Field(..., min_length=8)


class TokenVerifyRequest(BaseModel):
    """Схема запроса на валидацию токена."""
    token: str


class TokenVerifyResponse(BaseModel):
    """Схема ответа на валидацию токена."""
    valid: bool
    user_id: Optional[int] = None

