"""Pydantic модели для Core сервиса."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Общие типы ====================

class ScheduleType(str, Enum):
    IMMEDIATE = "immediate"
    INTERVALS = "intervals"


class TimeInterval(BaseModel):
    """Временной интервал в формате HH:MM."""
    start: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end: str = Field(..., pattern=r"^\d{2}:\d{2}$")


# ==================== Healthcheck ====================

class HealthcheckItem(BaseModel):
    """Результат проверки одного сервиса."""
    service_name: str
    status: str  # "ok" или "error"
    error: Optional[str] = None


class HealthcheckResponse(BaseModel):
    """Ответ с результатами healthcheck всех сервисов."""
    services: List[HealthcheckItem]


# ==================== Statistics ====================

class StatisticsItem(BaseModel):
    """Статистика по одному сервису/платформе."""
    service_name: str
    collected_posts: int
    processed_posts: int
    published_posts: int


class StatisticsResponse(BaseModel):
    """Ответ со статистикой всех сервисов."""
    services: List[StatisticsItem]


class UserStatisticsItem(BaseModel):
    """Статистика использования для одного пользователя."""
    user_id: int
    username: str
    email: str
    role: str
    total_posts: int
    collected_posts: int
    processed_posts: int
    published_posts: int


class UserStatisticsResponse(BaseModel):
    """Ответ со статистикой использования по пользователям."""
    users: List[UserStatisticsItem]


# ==================== Schedule Snapshots ====================

class ScheduleSnapshot(BaseModel):
    """Снимок расписания из таблицы schedule_snapshots."""
    user_id: int
    platform: str
    publish_enabled: bool
    collect_enabled: bool
    schedule_type: str
    time_intervals: List[Dict[str, Any]]
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleResponse(BaseModel):
    """Ответ со списком расписаний."""
    schedules: List[ScheduleSnapshot]


# ==================== Telegram ====================

class TelegramProfileBase(BaseModel):
    """Базовая модель профиля Telegram."""
    publish_enabled: bool = False
    collect_enabled: bool = False
    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    time_intervals: List[TimeInterval] = []
    api_id: Optional[str] = None
    api_hash: Optional[str] = None
    chats_to_read: List[str] = []
    save_conditions: List[str] = []
    channel_to_post: Optional[str] = None
    process_enabled: bool = False
    processing_description: Optional[str] = None


class TelegramProfileCreate(TelegramProfileBase):
    """Модель для создания/обновления профиля Telegram."""
    pass


class TelegramProfile(TelegramProfileBase):
    """Модель профиля Telegram с ID."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TelegramPost(BaseModel):
    """Модель поста для Telegram (max 4096 символов)."""
    text: str = Field(..., max_length=4096)
    to_tg: bool = True
    to_tw: bool = False
    to_wp: bool = False
    to_vk: bool = False


# ==================== Twitter ====================

class TwitterProfileBase(BaseModel):
    """Базовая модель профиля Twitter."""
    publish_enabled: bool = False
    collect_enabled: bool = False
    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    time_intervals: List[TimeInterval] = []
    use_proxy: bool = False
    proxy_user: Optional[str] = None
    proxy_pass: Optional[str] = None
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    twitter_username: Optional[str] = None
    twitter_password: Optional[str] = None


class TwitterProfileCreate(TwitterProfileBase):
    """Модель для создания/обновления профиля Twitter."""
    pass


class TwitterProfile(TwitterProfileBase):
    """Модель профиля Twitter с ID."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TwitterPost(BaseModel):
    """Модель поста для Twitter (max 280 символов)."""
    text: str = Field(..., max_length=280)
    to_tg: bool = False
    to_tw: bool = True
    to_wp: bool = False
    to_vk: bool = False


# ==================== WordPress ====================

class WordPressProfileBase(BaseModel):
    """Базовая модель профиля WordPress (legacy)."""
    publish_enabled: bool = False
    collect_enabled: bool = False
    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    time_intervals: List[TimeInterval] = []
    site_url: Optional[str] = None
    username: Optional[str] = None
    app_password: Optional[str] = None


class WordPressProfileCreate(WordPressProfileBase):
    """Модель для создания/обновления профиля WordPress (legacy)."""
    pass


class WordPressProfile(WordPressProfileBase):
    """Модель профиля WordPress с ID (legacy)."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordPressPublishProfileCreate(BaseModel):
    """Модель для создания/обновления профиля публикации WordPress.
    time_intervals — одно значение времени в формате "HH:MM".
    """
    publish_enabled: bool = False
    schedule_type: Optional[str] = "on_new_messages"
    time_intervals: Optional[str] = None  # "HH:MM"
    site_url: Optional[str] = None
    username: Optional[str] = None
    app_password: Optional[str] = None


class CollectSiteItem(BaseModel):
    """Один сайт сбора: site_url, schedule_type, time_intervals (HH:MM)."""
    site_url: Optional[str] = None
    schedule_type: Optional[str] = "on_new_messages"
    time_intervals: Optional[str] = None  # "HH:MM"


class WordPressCollectProfileCreate(BaseModel):
    """Модель для создания/обновления профиля сбора (parser) WordPress.
    collect_sites — список объектов с полями site_url, schedule_type, time_intervals (HH:MM).
    """
    collect_enabled: bool = False
    collect_sites: Optional[List[Dict[str, Any]]] = []  # [{site_url, schedule_type, time_intervals}]


class WordPressPostContent(BaseModel):
    """Вложенный объект post для реального WordPress."""
    title: str
    content: str = Field(..., max_length=150000)
    status: Optional[str] = None  # draft, publish, pending, private
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    excerpt: Optional[str] = None
    slug: Optional[str] = None
    featured_media: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None


class WordPressPost(BaseModel):
    """Тело запроса POST /wp/post из ui-app."""
    pageID: Optional[str] = None
    tagIdList: Optional[List[int]] = None
    categoriesIdList: Optional[List[int]] = None
    post: WordPressPostContent


# ==================== VKontakte ====================

class VKontakteProfileBase(BaseModel):
    """Базовая модель профиля VKontakte."""
    publish_enabled: bool = False
    collect_enabled: bool = False
    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    time_intervals: List[TimeInterval] = []
    owner_id: Optional[str] = None
    friends_only: bool = False
    from_group: bool = False
    message: Optional[str] = None
    attachments: Optional[str] = None
    signed: bool = False
    mark_as_ads: bool = False


class VKontakteProfileCreate(VKontakteProfileBase):
    """Модель для создания/обновления профиля VKontakte."""
    pass


class VKontakteProfile(VKontakteProfileBase):
    """Модель профиля VKontakte с ID."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VKontaktePost(BaseModel):
    """Модель поста для VKontakte (max 15985 символов)."""
    text: str = Field(..., max_length=15985)
    to_tg: bool = False
    to_tw: bool = False
    to_wp: bool = False
    to_vk: bool = True


# ==================== cURL ====================

class CurlSettingsBase(BaseModel):
    """Базовая модель настроек cURL скрапинга."""
    collect_enabled: bool = False
    schedule_type: str = "standard"  # "standard" или "intervals"
    time_intervals: List[TimeInterval] = []
    url: Optional[str] = None
    xpath: Optional[str] = None
    take_screenshot: bool = False
    to_tg: bool = False
    to_tw: bool = False
    to_vk: bool = False
    to_wp: bool = False


class CurlSettingsCreate(CurlSettingsBase):
    """Модель для создания/обновления настроек cURL."""
    pass


class CurlSettings(CurlSettingsBase):
    """Модель настроек cURL с ID."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== cPost (ручные посты) ====================

class DefaultPlatforms(BaseModel):
    """Платформы по умолчанию для ручных постов."""
    tg: bool = False
    tw: bool = False
    wp: bool = False
    vk: bool = False


class CpostProfileBase(BaseModel):
    """Базовая модель профиля ручных постов."""
    default_platforms: DefaultPlatforms = DefaultPlatforms()


class CpostProfileCreate(CpostProfileBase):
    """Модель для создания/обновления профиля ручных постов."""
    pass


class CpostProfile(CpostProfileBase):
    """Модель профиля ручных постов с ID."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CpostPost(BaseModel):
    """Модель ручного поста (max 150000 символов)."""
    text: str = Field(..., max_length=150000)
    title: Optional[str] = None
    to_tg: bool = False
    to_tw: bool = False
    to_wp: bool = False
    to_vk: bool = False


# ==================== Post (общая модель) ====================

class PostBase(BaseModel):
    """Базовая модель поста."""
    domain: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    avatar: Optional[str] = None
    post_date: Optional[datetime] = None
    post_text: str
    screenshot: Optional[str] = None
    images: List[str] = []
    image_over_text: Optional[str] = None
    comments: int = 0
    reposts: int = 0
    likes: int = 0
    views: int = 0
    is_ad: bool = False
    status: str = "collected"
    post_type: Optional[str] = None
    to_tg: bool = False
    to_tw: bool = False
    to_wp: bool = False
    to_vk: bool = False


class PostCreate(PostBase):
    """Модель для создания поста."""
    pass


class Post(PostBase):
    """Модель поста с ID."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Notifications ====================

class NotificationCreate(BaseModel):
    """Модель для создания уведомления."""
    message: str = Field(..., min_length=1)


class Notification(BaseModel):
    """Модель уведомления."""
    id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Ответ со списком уведомлений."""
    notifications: List[Notification]
