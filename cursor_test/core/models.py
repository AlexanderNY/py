"""SQL-определения таблиц для Core сервиса."""

# Таблица posts - общая для всех постов
POSTS_TABLE = """
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    domain VARCHAR(255),
    url TEXT,
    title VARCHAR(500),
    author VARCHAR(255),
    avatar TEXT,
    post_date TIMESTAMP,
    post_text TEXT,
    screenshot TEXT,
    images JSONB DEFAULT '[]',
    image_over_text TEXT,
    comments INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    is_ad BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'collected',
    post_type VARCHAR(50),
    to_tg BOOLEAN DEFAULT FALSE,
    to_tw BOOLEAN DEFAULT FALSE,
    to_wp BOOLEAN DEFAULT FALSE,
    to_vk BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Индексы для posts
POSTS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);
"""

# Таблица tg_profiles - настройки Telegram по пользователям
TG_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS tg_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    publish_enabled BOOLEAN DEFAULT FALSE,
    collect_enabled BOOLEAN DEFAULT FALSE,
    schedule_type VARCHAR(20) DEFAULT 'immediate',
    time_intervals JSONB DEFAULT '[]',
    api_id VARCHAR(50),
    api_hash VARCHAR(100),
    chats_to_read JSONB DEFAULT '[]',
    save_conditions JSONB DEFAULT '[]',
    channel_to_post VARCHAR(50),
    process_enabled BOOLEAN DEFAULT FALSE,
    processing_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Таблица tw_profiles - настройки Twitter
TW_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS tw_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    publish_enabled BOOLEAN DEFAULT FALSE,
    collect_enabled BOOLEAN DEFAULT FALSE,
    schedule_type VARCHAR(20) DEFAULT 'immediate',
    time_intervals JSONB DEFAULT '[]',
    use_proxy BOOLEAN DEFAULT FALSE,
    proxy_user VARCHAR(100),
    proxy_pass VARCHAR(100),
    proxy_host VARCHAR(255),
    proxy_port INTEGER,
    twitter_username VARCHAR(100),
    twitter_password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Таблица wp_profiles - настройки WordPress
WP_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS wp_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    publish_enabled BOOLEAN DEFAULT FALSE,
    collect_enabled BOOLEAN DEFAULT FALSE,
    schedule_type VARCHAR(20) DEFAULT 'immediate',
    time_intervals JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Таблица vk_profiles - настройки VKontakte
VK_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS vk_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    publish_enabled BOOLEAN DEFAULT FALSE,
    collect_enabled BOOLEAN DEFAULT FALSE,
    schedule_type VARCHAR(20) DEFAULT 'immediate',
    time_intervals JSONB DEFAULT '[]',
    owner_id VARCHAR(50),
    friends_only BOOLEAN DEFAULT FALSE,
    from_group BOOLEAN DEFAULT FALSE,
    message TEXT,
    attachments TEXT,
    signed BOOLEAN DEFAULT FALSE,
    mark_as_ads BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Таблица curl_settings - настройки cURL скрапинга
CURL_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS curl_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    collect_enabled BOOLEAN DEFAULT FALSE,
    schedule_type VARCHAR(20) DEFAULT 'standard',
    time_intervals JSONB DEFAULT '[]',
    url TEXT,
    xpath TEXT,
    take_screenshot BOOLEAN DEFAULT FALSE,
    to_tg BOOLEAN DEFAULT FALSE,
    to_tw BOOLEAN DEFAULT FALSE,
    to_vk BOOLEAN DEFAULT FALSE,
    to_wp BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Таблица cpost_profiles - настройки ручных постов
CPOST_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS cpost_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    default_platforms JSONB DEFAULT '{"tg": false, "tw": false, "wp": false, "vk": false}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Список всех таблиц для инициализации
ALL_TABLES = [
    POSTS_TABLE,
    POSTS_INDEXES,
    TG_PROFILES_TABLE,
    TW_PROFILES_TABLE,
    WP_PROFILES_TABLE,
    VK_PROFILES_TABLE,
    CURL_SETTINGS_TABLE,
    CPOST_PROFILES_TABLE,
]
