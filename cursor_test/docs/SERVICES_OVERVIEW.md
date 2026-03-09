# Обзор сервисов: UI, API Gateway, эндпоинты и доступ к БД

## 1. Запросы с UI

UI использует `apiClient` с `baseURL: '/api'`. Vite proxy перенаправляет `/api` на API Gateway и убирает префикс `/api`, поэтому фактические запросы идут на Gateway по путям без `/api`.

### 1.1 Auth (auth-service.ts)

| Метод | Путь (от UI) | Описание |
|-------|----------------|----------|
| POST | `/auth/login` | Вход |
| POST | `/auth/register` | Регистрация |
| POST | `/auth/logout` | Выход (тело: `refresh_token`) |
| POST | `/auth/all-logout` | Выход со всех устройств |
| GET | `/auth/profile` | Профиль пользователя |
| POST | `/auth/profile` | Обновление профиля |
| POST | `/auth/reset-password` | Запрос сброса пароля |
| POST | `/auth/reset-password/confirm` | Подтверждение сброса пароля |
| POST | `/auth/refresh` | Обновление пары токенов |
| POST | `/auth/verify` | Верификация email (код) |
| GET | `/auth/users` | Список пользователей (admin) |

### 1.2 Core (core-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/core/healthchecks` | Healthcheck всех сервисов |
| GET | `/core/statistics` | Статистика |
| GET | `/core/users-statistics` | Статистика по пользователям (admin) |
| GET | `/core/schedule` | Расписания из schedule_snapshots (admin) |
| POST | `/core/start-discovery` | Запуск цикла сбора расписаний (admin) |
| POST | `/core/start-bot` | Запуск ботов по платформам (admin) |

### 1.3 Create Post (create-post-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/cpost/profile` | Профиль ручных постов (default_platforms) |
| POST | `/cpost/profile` | Сохранение профиля |
| GET | `/cpost/posts` | Список ручных постов |
| GET | `/cpost/post/{id}` | Один пост |
| POST | `/cpost/post` | Создание поста |
| PUT | `/cpost/post/{id}` | Обновление поста |
| DELETE | `/cpost/post/{id}` | Удаление поста |

### 1.4 Custom URL (custom-url-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/curl/settings` | Настройки cURL/скрапинга по URL |
| POST | `/curl/settings` | Сохранение настроек |

### 1.5 Notifications (notifications-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/core/notifications` | Список уведомлений |
| POST | `/core/notifications` | Создание уведомления (admin) |
| DELETE | `/core/notifications/{id}` | Удаление уведомления (admin) |

### 1.6 Telegram (telegram-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/tg/profile` | Профиль Telegram |
| POST | `/tg/profile` | Сохранение профиля |
| GET | `/tg/posts` | Список постов TG |
| GET | `/tg/post/{id}` | Один пост |
| POST | `/tg/post` | Создание поста (multipart: text, image) |
| PUT | `/tg/post/{id}` | Обновление поста |
| DELETE | `/tg/post/{id}` | Удаление поста |

### 1.7 Twitter (twitter-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/tw/profile` | Профиль Twitter |
| POST | `/tw/profile` | Сохранение профиля |
| POST | `/tw/post` | Создание поста |

### 1.8 VKontakte (vkontakte-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/vk/profile` | Профиль VK |
| POST | `/vk/profile` | Сохранение профиля |
| POST | `/vk/post` | Создание поста |

### 1.9 WordPress (wordpress-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET/POST | `/wp/profile` | Профиль WordPress |
| GET/POST | `/wp/publish-profile` | Профиль публикации |
| GET/POST | `/wp/collect-profile` | Профиль сбора |
| GET | `/wp/profiles` | Все профили WP |
| GET | `/wp/posts` | Список постов WP |
| GET | `/wp/post/{id}` | Один пост |
| POST | `/wp/post` | Создание поста |
| PUT | `/wp/post/{id}` | Обновление поста |
| DELETE | `/wp/post/{id}` | Удаление поста |

### 1.10 Test / SelectCB (test-service.ts)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/test/products` | Список продуктов |
| GET | `/test/search/{orderId}` | Поиск заказа |
| POST | `/test/submit` | Создание заказа |

---

## 2. API Gateway — маршрутизация и правила

- **Порт:** 8000  
- **Поведение:** проксирование запросов в сервисы, добавление заголовков `X-User-Id` и `X-User-Role` из JWT.
- **Публичные пути (без JWT):**  
  `/auth/login`, `/auth/register`, `/auth/refresh`, `/auth/verify`, `/auth/reset-password`, `/auth/reset-password/confirm`, `/health`.
- **Rate limiting:** задаётся в `api-gateway/config.py` по путям (логин, регистрация, core, боты и т.д.).

### 2.1 Роутеры и маппинг на сервисы

| Префикс Gateway | Целевой сервис | Назначение |
|-----------------|----------------|------------|
| `/auth` | Auth (8001) | Регистрация, логин, профиль, refresh, logout, verify, reset-password, users |
| `/core` | Core (8002) или Scheduler (8003) | Статистика, healthcheck, расписания, discovery, start-bot, уведомления |
| `/wp` | Core | WordPress профили и посты |
| `/tg` | Core | Telegram профили и посты |
| `/tw` | Core | Twitter профили и посты |
| `/vk` | Core | VK профили и посты |
| `/curl` | Core | Настройки cURL/скрапинга |
| `/cpost` | Core | Ручные посты (профиль, CRUD постов) |
| `/tg-bot/schedule` | TG Bot (8004) | POST → `/schedule` |
| `/wp-bot/schedule` | WP Bot (8006) | POST → `/schedule` |
| `/vk-bot/schedule` | VK Bot (8005) | POST → `/schedule` |
| `/url-bot/schedule` | URL Bot (8007) | POST → `/schedule` |
| `/url-bot/run` | URL Bot (8007) | POST → `/run` (без JWT) |
| `/test` | SelectCB (8008) | products, search, submit |
| Stubs | — | `/scheduler/*`, `/tg-bot/*`, `/vk-bot/*`, `/wp-bot/*`, `/url-bot/*` — ответ 501 |

### 2.2 Особенности маппинга

- `POST /auth/profile` на Gateway → `PUT /profile` на Auth.
- `GET /core/healthcheck` на Gateway → `GET /healthchecks` на Core.
- У большинства маршрутов (кроме публичных и `/url-bot/run`) используется `Depends(get_current_user)` — требуется JWT.

---

## 3. Эндпоинты по сервисам

### 3.1 Auth (порт 8001)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Корень |
| GET | `/health` | Health |
| POST | `/register` | Регистрация |
| POST | `/login` | Вход |
| POST | `/refresh` | Обновление токенов |
| POST | `/logout` | Выход |
| GET | `/profile` | Профиль |
| PUT | `/profile` | Обновление профиля |
| GET | `/users` | Список пользователей (admin) |
| GET | `/verify/{token}` | Верификация email по токену |
| POST | `/verify-token` | Проверка токена (для других сервисов) |
| POST | `/reset-password` | Инициация сброса пароля |
| POST | `/reset-password/confirm` | Подтверждение сброса |
| POST | `/all_logout` | Выход со всех устройств |

### 3.2 Core (порт 8002)

| Префикс | Метод | Путь (относительно префикса) | Описание |
|---------|--------|------------------------------|----------|
| — | GET | `/healthchecks` | Healthcheck всех сервисов |
| — | GET | `/statistics` | Статистика |
| — | GET | `/users-statistics` | Статистика по пользователям |
| — | GET | `/schedules` | Сводка расписаний (для scheduler) |
| — | GET | `/schedule` | Расписания из schedule_snapshots (admin) |
| `/tg` | GET/POST | `/profile` | Профиль Telegram |
| `/tg` | GET | `/profiles` | Все TG-профили |
| `/tg` | GET/POST | `/post`, `/posts`, `/post/{id}` | CRUD постов TG |
| `/tw` | GET/POST | `/profile`, `/profiles`, `/post` | Twitter |
| `/vk` | GET/POST | `/profile`, `/profiles`, `/post` | VK |
| `/wp` | GET/POST | `/profile`, `/publish-profile`, `/collect-profile`, `/profiles` | Профили WP |
| `/wp` | GET/POST/PUT/DELETE | `/post`, `/posts`, `/post/{id}` | Посты WP |
| `/curl` | GET/POST | `/settings` | Настройки cURL |
| `/cpost` | GET/POST | `/profile` | Профиль ручных постов |
| `/cpost` | GET/POST/PUT/DELETE | `/posts`, `/post`, `/post/{id}` | Ручные посты |
| `/notifications` | GET/POST/DELETE | ``, `/{id}` | Уведомления |

Идентификация пользователя в Core: заголовки `X-User-Id`, `X-User-Role` (проставляются Gateway из JWT).

### 3.3 Scheduler (порт 8003)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/`, `/health` | Корень и health |
| POST | `/start-discovery` | Один цикл сбора расписаний (JWT) |
| GET | `/schedules` | Получение и сохранение расписаний (JWT) |
| POST | `/start-bot` | Запуск ботов по платформам (JWT) |

### 3.4 TG Bot (порт 8004)

| Префикс | Метод | Путь | Описание |
|---------|--------|------|----------|
| `/tg` | — | — | Роутер с prefix `/tg` |
| `/tg/auth` | POST | `/code` | Код подтверждения |
| `/tg/auth` | POST | `/password` | 2FA пароль |
| `/tg/auth` | GET | `/status/{user_id}` | Статус авторизации |
| — | GET | `/health` | Health |

Через Gateway вызывается только `POST /tg-bot/schedule` → `POST /schedule` на боте. В текущем коде tg-bot зарегистрирован только роутер `auth` (prefix `/tg`, эндпоинты `/tg/auth/code`, `/tg/auth/password`, `/tg/auth/status/{user_id}`). Эндпоинт `POST /schedule` для приёма команд от scheduler в репозитории не реализован (возможен в другой ветке или по плану).

### 3.5 URL Bot (порт 8007)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/`, `/health` | Корень и health |
| POST | `/run` | Тестовый запуск скрапинга (url, xpath, take_screenshot) |
| POST | `/schedule` | Обработка расписаний от scheduler (platform=url) |

### 3.6 SelectCB / Test (порт 8008)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/`, `/health` | Корень и health |
| GET | `/test/products` | Список продуктов |
| GET | `/test/search/{order_id}` | Поиск заказа |
| POST | `/test/submit` | Создание заказа |

---

## 4. Базы данных и таблицы по сервисам

### 4.1 Общая схема

- **auth**, **core**, **scheduler**, **tg-bot** в конфигах по умолчанию используют одну БД: **db_bot** (PostgreSQL).  
- **core** в docker-compose имеет `DB_NAME=core_db`, но в `core/config.py` по умолчанию задан `DATABASE_URL` с `dbname=db_bot`, то есть фактически та же БД.  
- **selectcb** использует отдельную БД (тот же хост, в конфиге по умолчанию тоже **db_bot** — при необходимости можно вынести в отдельную БД через `DATABASE_URL`).  
- **url-bot** своей БД не использует.

### 4.2 Auth

- **БД:** `db_bot` (из `DATABASE_URL`, docker: `host.docker.internal`).
- **Таблицы:**  
  `users`, `refresh_tokens`, `blacklisted_tokens`, `password_reset_tokens`, `email_verification_tokens`.

### 4.3 Core

- **БД:** `db_bot` (из `core/config.py`).
- **Таблицы:**  
  `posts`, `tg_profiles`, `tg_posts`, `tw_profiles`, `wp_profiles`, `wp_publish_profile`, `wp_collect_profile`, `wp_collect_sites`, `wp_posts`, `vk_profiles`, `curl_settings`, `cpost_profiles`, `notifications`.  
- **Чтение:** также читает таблицу **`schedule_snapshots`**, которая создаётся и заполняется сервисом **scheduler** в той же БД.

### 4.4 Scheduler

- **БД:** `db_bot` (из `DATABASE_URL` в docker-compose).
- **Таблицы:**  
  `schedule_snapshots`, `schedule_snapshots_wp`.

### 4.5 TG Bot

- **БД:** `db_bot` (из `tg-bot/config.py`). Таблицы не создаёт сам сервис (используются таблицы core, в т.ч. **tg_profiles** для статуса авторизации).

### 4.6 URL Bot

- **БД:** нет. Работает только с Core/API по HTTP (скрапинг, вызов `/run` и `/schedule`).

### 4.7 SelectCB (Test)

- **БД:** в конфиге по умолчанию `db_bot` (можно задать отдельную через `DATABASE_URL`).
- **Таблицы:**  
  `products`, `orders`, `orderdetails`.

---

## 5. Сводная таблица доступа к БД

| Сервис    | База данных | Таблицы (создание/использование) |
|-----------|-------------|-----------------------------------|
| Auth      | db_bot      | users, refresh_tokens, blacklisted_tokens, password_reset_tokens, email_verification_tokens |
| Core      | db_bot      | posts, tg_profiles, tg_posts, tw_profiles, wp_*, vk_profiles, curl_settings, cpost_profiles, notifications; чтение: schedule_snapshots |
| Scheduler | db_bot      | schedule_snapshots, schedule_snapshots_wp |
| TG Bot    | db_bot      | чтение/запись tg_profiles (и др. при необходимости) |
| URL Bot   | —           | нет |
| SelectCB  | db_bot*     | products, orders, orderdetails |

\* При необходимости SelectCB можно переключить на отдельную БД через `DATABASE_URL`.
