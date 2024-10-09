# Backend_Cyberzone
Тестовое задание для отдела IT Киберзоны
## Содержание

- [Требования](#требования)
- [Установка](#установка)
- [Запуск](#запуск)
- [API Документация](#api-документация)


## Требования

Перед тем, как запустить проект, убедитесь, что у вас установлены следующие зависимости:

- Python 3.10 или выше
- PostgreSQL


## Установка

1. Склонируйте репозиторий на локальный компьютер:

```bash
git clone [https://github.com/ваше_имя_пользователя/backend-fastapi.git](https://github.com/Komissarich/Backend_Cyberzone)
cd Backend-Cyberzone
```
## Запуск
1. Убедитесь, что у вас установлен Docker. Запустите Docker Engine

2. Запустите проект:
 ```bash
docker-compose up --build
```
Важно! Если у вас выскочит ошибка вида ![image](https://github.com/user-attachments/assets/fc5045f7-11a6-4fef-aee2-3406afea9f5c), тогда просто выполните команду docker-compose down, а затем снова запустите проект с помощью docker-compose up.

3. Обратиться к Api можно через адресную строку браузера (localhost:8010/api) или же через программу Postman (http://127.0.0.1:8010/api)


## API Документация

Документация по API находится в папке swagger в файле openapi.yml. Для удобного просмотра откройте его на сайте https://editor.swagger.io/

