# 🛒 Smart Grocery Sync

Умный список покупок: Telegram-бот с AI-парсингом, FastAPI бэкенд и React-фронтенд.

## Архитектура

```
┌─────────────┐     POST /api/items      ┌──────────┐
│  Telegram   │ ──────────────────────►   │          │
│  Bot (aiogram + OpenAI)                │ Backend  │
└─────────────┘                          │ FastAPI  │
                                         │          │
┌─────────────┐     GET/PATCH /api/items │          │
│  Frontend   │ ◄──────────────────────► │          │
│  React+Vite │                          └────┬─────┘
└─────────────┘                               │
                                              │
                                       ┌──────▼──────┐
                                       │  PostgreSQL  │
                                       └─────────────┘
```

## Структура проекта

```
.
├── backend/               # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py        # Точка входа, CORS, lifespan
│   │   ├── config.py      # Настройки из .env
│   │   ├── database.py    # Async engine, сессия
│   │   ├── models/item.py # SQLAlchemy модель
│   │   ├── schemas/item.py# Pydantic схемы
│   │   └── routers/items.py # API роуты
│   ├── requirements.txt
│   └── Dockerfile
├── bot/                   # Telegram-бот (Nanobot)
│   ├── main.py            # aiogram + OpenAI parsing
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx        # Главный компонент
│   │   ├── api.js         # Axios API клиент
│   │   ├── main.jsx       # Entry point
│   │   └── index.css      # Tailwind стили
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf         # Nginx для production
│   ├── Dockerfile         # Multi-stage build
│   └── postcss.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

## Быстрый старт

### 1. Настройка .env

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите:
- `TG_BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
- `OPENROUTER_API_KEY` — ключ от [OpenRouter](https://openrouter.ai/) (есть бесплатные модели)

> **OpenRouter**: зарегистрируйтесь на openrouter.ai, создайте API key.
> Бесплатные модели: `google/gemma-2-9b-it:free`, `meta-llama/llama-3.3-8b-instruct:free`.
> Модель можно сменить через параметр `LLM_MODEL` в `.env`.

### 2. Запуск

```bash
docker compose up --build
```

### 3. Доступ

| Сервис | URL |
|---|---|
| Фронтенд | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Использование

### Через Telegram-бота

1. Откройте вашего бота в Telegram
2. Напишите: `Купи яблоки, молоко, хлеб и курицу`
3. Бот распознает продукты, распределит по категориям и сохранит в БД
4. Откройте фронтенд — товары уже в списке

### Через фронтенд

1. Откройте http://localhost:3000
2. Добавьте товар вручную через форму
3. Отмечайте купленные товары чекбоксами

### Через API

```bash
# Получить список
curl http://localhost:8000/api/items/1

# Добавить товар
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Хлеб", "category": "Бакалея", "user_id": 1}'

# Инвертировать статус
curl -X PATCH http://localhost:8000/api/items/1
```

## Технологии

| Компонент | Стек |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), asyncpg |
| Database | PostgreSQL 16 |
| Bot | aiogram 3.x, OpenRouter (Llama 3.1 8B free) |
| Frontend | React 18, Vite, Tailwind CSS, Axios |
| DevOps | Docker, Docker Compose, Nginx (multi-stage) |

## API Reference

| Метод | Endpoint | Описание |
|---|---|---|
| `GET` | `/api/items/{user_id}` | Список товаров пользователя |
| `POST` | `/api/items/` | Добавить товар `{name, category, user_id}` |
| `PATCH` | `/api/items/{item_id}` | Инвертировать `is_bought` |
| `GET` | `/health` | Health check |
