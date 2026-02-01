# todo здесь собираем список долгосрочных задач

посмотри роуты с гейтвэя

# todo Изменить UI в сторону единообразия
1 для каждого раздела соцсетей
    1.1 Profile Settings отдельный tab
    1.2 поля Profile Settings требуется предзаполнить данными из базы данных
    1.3 Create Post сообщения в отдельный tab
    1.4 Posts отдельный tab для списка всех сообщений из бд и их статуса, по клику на строку загрузить данные строки в редактор постов

2 таблицу posts разделить на множество таблиц для каждой соцсети
    3.1 wp
        tab Create Post
        title: Заголовок поста
        content: Содержимое поста (добавь к полю простой html редактор с возможностью менять форматирование текста)
        status: Статус поста (select: draft, publish, pending, private)
        categories: Список ID категорий
        tags: Список ID тегов
        excerpt: Краткое описание
        slug: URL slug поста
        featured_media: ID медиа-файла для обложки
        meta: Дополнительные мета-поля
        
        при submit
        Post /wp/post на api gateway

        tab Profile Settings
        site_url: URL сайта WordPress
        username: Имя пользователя WordPress
        app_password: Application Password 
        Enable publishing
        Enable collection
        Publish Schedule

        tab Posts
        вывести таблицу всех постов с эого аккаунта
        title
        status
        excerpt

        при загрузке
        GET /wp/posts на api gateway
        
        при загрузке
        GET /wp/profile  на api gateway
        при submit
        POST /wp/profile  на api gateway



    3.2 tg
    tab Create Post

    tab Profile Settings
        API Credentials
            api_id
            api_hash
        Enable publishing
        Enable collection
        Publish Schedule
    tab Posts

    3.3 tw
    tab Create Post
    tab Profile Settings
    tab Posts
    3.4 vk
    tab Create Post
    tab Profile Settings
    tab Posts
    3.5 tr
    tab Create Post
    tab Profile Settings
    tab Posts
    3.6 in
    tab Create Post
    tab Profile Settings
    tab Posts

5 добавить возможность передачи изображения в каждом посте
6 возможность вести несколько сайтов/тг каналов
7 разобраться с падением сервиса авторизации
8 организовать отдельно вычитку и постинг

# todo вынести в конфигуационные файлы переменные, пути к сервисам, JWT ключ шифрования
# todo выписать все запросы сервисов для подготовки тестирования API
# todo Перерисовать архитектуру сервиса  

# todo собирать статистику "успешно gathered" и "успешно posted" в отдельную таблицу

# todo twitter does't work via proxy
# todo proxy перенести в настройки профиля
# todo gather used CPU, Memory and Network
# todo определить условия для асинхронного запуска функций бота
# todo определить условия для запуска нескольких экземпляров бота единовременно

# todo тут требуется тест с парсером selenium не будет ли конфликта при частых циклах (если уже запущен сбрщик)
# todo тут требуется тест с teegraph, выцепит ли он сообщения если сборщик на паузе (например стоит цикл проверки раз в час)
# Повторяется цикл раз в n секунд, например 300, но кажется излише часто (3600 секунд = 1 час, 14400 секунд = 4 часа)
# todo собрать посты со SmartLab для примера

# todo в JWT должна присутствовать роль и тарифный план
# todo тарифные планы и сервис оплат
# нейросеть для обаботки сообщений




Как ограничивить постинг и скрэпинг?
может стоит в админке ставить цифру сколько

еще требуется галка обрабатывать или нет и отдельный таб для обработки

GET /wp/post/{post_id} — один пост.
PUT /wp/post/{post_id} — обновление поста.
DELETE /wp/post/{post_id} — пометка поста как удалённого (status = deleted).



!!!! проверить исходящие запросы! что то шлет во вне

теперь конфигурации также требуется скорректировать профили
