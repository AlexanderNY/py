Требуется создать сервис api gateway для перенаправления запросов от сервиса к сервису со следующим функционалом:
CORS
    доступ get post разрешен с сервиса ui-app
    URL остальных сервисов должны быть перечислены в конфигурационном файле  
маршрутизация запросов
    сервис auth
        перенаправить запросы с сервиса ui-app на сервис auth
        запрос с ui-app post /auth/register нужно преобразовать в post /register на сервис auth
        запрос с ui-app post /auth/login нужно преобразовать в post /login на сервис auth
        запрос с ui-app post /auth/refresh нужно преобразовать в post /refresh на сервис auth
        запрос с ui-app post /auth/logout нужно преобразовать в post /logout на сервис auth
        запрос с ui-app get /auth/profile нужно преобразовать в get /profile на сервис auth
        запрос с ui-app post /auth/profile нужно преобразовать в put /profile на сервис auth
        запрос с ui-app post /auth/verify нужно преобразовать в post /verify на сервис auth
        запрос с ui-app post /auth/reset-password нужно преобразовать в post /reset-password на сервис auth      
        запрос с ui-app post /auth/all-logout нужно преобразовать в post /all-logout на сервис auth             
    сервис core
    сервис scheduler
    сервис tg-bot
    сервис vk-bot
    сервис wp-bot
    сервис url-bot
    
аутентификация и авторизация
    запрос пользоватля должен быть с JWT токеном в header
ограничение частоты запросов (Rate Limiting)
    требуется ограничение числа запросов накаждый endpoint со стороны API Gateway
    ограничения должны храниться в конфигурационно файле

