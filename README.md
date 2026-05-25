# API ежедневного планировщика

Приложение на FastAPI для планирование задач:  демонстрирует регистрацию, вход/выход, работу через сессионные куки и ролевой моделью (USER, STAFF, ADMIN). Стек: async SQLAlchemy, PostgreSQL, uvicorn.


## Технологии

- **FastAPI** - веб-фреймворк
- **asyncio** - асинхонный код
- **PostgreSQL** - база данных
- **SQLAlchemy 2.0** - ORM (асинхронный)
- **Alembic** - миграции
- **Docker** - контейнеризация
- **Pytest** - тестирование
- **UV** - менеджер пакетов


## Запуск через Docker 
### Предварительные требования

- Установленный [Docker](https://www.docker.com/products/docker-desktop/)

### 1. Клонировать репозиторий

```
git clone https://github.com/1alexvlad/daily-journal-api
cd daily-planner
```
### Запустить приложение
```
docker-compose up --build
```

## После запуска API будет доступно по адресу: http://localhost:8000/docs



### Эндпоинты
- POST /auth/register - регистрация
- POST /auth/login - вход
- POST /auth/logout - выход
- GET /auth/me - информация о пользователе
- GET /auth//id/{user_id} - информация о пользователе по id для ролей STAFF и ADMIN
- GET /auth/all - отображение всех пользователей для ролей STAFF и ADMIN
- POST /auth/update - обновление пользователя 
- DELETE /auth/ - удаление пользователя 
- ------------
- GET /entries/ - список заметок
- POST /entries/ - создать заметку
- PUT /entries/{id} - изменить заметку по id
- DELETE /entries/{id} - удалить заметку по id


## Структура проекта
```
daily-planner/
├── app/
│   ├── admin/          # SQLAdmin панель
│   ├── core/           # Конфиги, security
│   ├── models/         # SQLAlchemy модели
│   ├── routers/        # API эндпоинты
│   ├── schemas/        # Pydantic схемы
│   ├── services/       # Бизнес-логика
│   ├── tests/          # Тесты
│   ├── main.py         # Точка входа
│   ├── config.py       # Настройки
│   └── database.py     # Подключение к БД
│   └── exceptions.py   # Ошибки
├── alembic/            # Миграции
├── .env                # Переменные окружения
├── docker-compose.yml  # Docker Compose
├── Dockerfile          # Docker образ
├── pyproject.toml      # Зависимости
└── README.md           # Этот файл
```