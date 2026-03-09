from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal, List


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
    role: Literal["guest", "user", "admin", "manager", "author"]
    tariff: str = "free"
    is_email_verified: bool
    created_at: datetime
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    role_in_group: Optional[Literal["manager", "author"]] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Схема для обновления профиля пользователя."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class AdminUserUpdate(BaseModel):
    """Схема для обновления роли и тарифа пользователя (только для администраторов)."""
    role: Optional[Literal["guest", "user", "admin", "manager", "author"]] = None
    tariff: Optional[str] = Field(None, max_length=50)


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


class GroupCreate(BaseModel):
    """Схема создания группы (менеджер или admin)."""
    name: str = Field(..., min_length=1, max_length=255)


class GroupUpdate(BaseModel):
    """Схема обновления названия группы."""
    name: str = Field(..., min_length=1, max_length=255)


class GroupMemberResponse(BaseModel):
    """Участник группы в ответе API."""
    user_id: int
    username: str
    email: str
    tariff: str
    role_in_group: Literal["manager", "author"]
    joined_at: datetime

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    """Группа в ответе API."""
    id: int
    name: str
    created_at: datetime
    created_by_user_id: Optional[int] = None
    role_in_group: Optional[Literal["manager", "author"]] = None
    members: Optional[List["GroupMemberResponse"]] = None

    class Config:
        from_attributes = True


class AddMemberRequest(BaseModel):
    """Добавление участника по email."""
    email: str = Field(..., min_length=1)


class RoleTariffHistoryEntry(BaseModel):
    """Запись истории изменения роли и тарифа пользователя."""
    id: int
    user_id: int
    changed_at: datetime
    changed_by_user_id: Optional[int] = None
    role_old: Optional[str] = None
    role_new: Optional[str] = None
    tariff_old: Optional[str] = None
    tariff_new: Optional[str] = None

    class Config:
        from_attributes = True

