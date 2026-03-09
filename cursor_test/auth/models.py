"""SQL схемы для создания таблиц базы данных."""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'guest' NOT NULL CHECK (role IN ('guest', 'user', 'admin', 'manager', 'author')),
    tariff VARCHAR(50) DEFAULT 'free' NOT NULL,
    is_email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

ADD_TARIFF_TO_USERS = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS tariff VARCHAR(50) DEFAULT 'free' NOT NULL;
"""

CREATE_REFRESH_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_BLACKLISTED_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS blacklisted_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_PASSWORD_RESET_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_EMAIL_VERIFICATION_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_USER_ROLE_TARIFF_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS user_role_tariff_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    role_old VARCHAR(20) NULL,
    role_new VARCHAR(20) NULL,
    tariff_old VARCHAR(50) NULL,
    tariff_new VARCHAR(50) NULL
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_blacklisted_tokens_token ON blacklisted_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_user_role_tariff_history_user_id ON user_role_tariff_history(user_id);
"""

ALTER_USERS_ROLE_CHECK = """
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('guest', 'user', 'admin', 'manager', 'author'));
"""

CREATE_GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL
);
"""

CREATE_GROUP_MEMBERS_TABLE = """
CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_in_group VARCHAR(20) NOT NULL CHECK (role_in_group IN ('manager', 'author')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
"""

CREATE_GROUP_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_group_members_group_id ON group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_group_members_user_id ON group_members(user_id);
"""

ALL_TABLES = [
    CREATE_USERS_TABLE,
    ADD_TARIFF_TO_USERS,
    CREATE_USER_ROLE_TARIFF_HISTORY_TABLE,
    ALTER_USERS_ROLE_CHECK,
    CREATE_GROUPS_TABLE,
    CREATE_GROUP_MEMBERS_TABLE,
    CREATE_GROUP_INDEXES,
    CREATE_REFRESH_TOKENS_TABLE,
    CREATE_BLACKLISTED_TOKENS_TABLE,
    CREATE_PASSWORD_RESET_TOKENS_TABLE,
    CREATE_EMAIL_VERIFICATION_TOKENS_TABLE,
    CREATE_INDEXES,
]

