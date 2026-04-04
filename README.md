# 🛒 Smart Grocery Sync

Smart grocery list with AI-powered Telegram bot, FastAPI backend, and React frontend.

## Architecture

```
┌─────────────┐     POST /api/items      ┌──────────┐
│  Telegram   │ ──────────────────────►   │          │
│  Bot (aiogram + OpenRouter)            │ Backend  │
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

## Project Structure

```
.
├── backend/               # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py        # Entry point, CORS, lifespan
│   │   ├── config.py      # Settings from .env
│   │   ├── database.py    # Async engine, session
│   │   ├── models/item.py # SQLAlchemy model
│   │   ├── schemas/item.py# Pydantic DTOs
│   │   └── routers/items.py # API routes
│   ├── requirements.txt
│   └── Dockerfile
├── bot/                   # Telegram bot (Nanobot)
│   ├── main.py            # aiogram + LLM parsing
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx        # Main component
│   │   ├── api.js         # Axios API client
│   │   ├── main.jsx       # Entry point
│   │   └── index.css      # Tailwind styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf         # Nginx for production
│   ├── Dockerfile         # Multi-stage build
│   └── postcss.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### 1. Configure .env

```bash
cp .env.example .env
```

Edit `.env` and provide:
- `TG_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
- `OPENROUTER_API_KEY` — from [OpenRouter](https://openrouter.ai/) (free models available)

> **OpenRouter**: register at openrouter.ai, create an API key.
> Free models: `google/gemma-2-9b-it:free`, `qwen/qwen3.6-plus:free`.
> Change the model via `LLM_MODEL` in `.env`.

### 2. Run

```bash
docker compose up --build
```

### 3. Access

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Usage

### Via Telegram Bot

1. Open your bot in Telegram
2. Write: `Buy apples, milk, bread, and chicken`
3. The bot parses products, categorizes them, and saves to the database
4. Open the frontend — items are already in the list

### Via Frontend

1. Open http://localhost:3000
2. Add items manually via the form
3. Toggle bought items with checkboxes

### Via API

```bash
# Get list
curl http://localhost:8000/api/items/1

# Add an item
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bread", "category": "Grocery", "user_id": 1}'

# Toggle bought status
curl -X PATCH http://localhost:8000/api/items/1
```

## Tech Stack

| Component | Stack |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), asyncpg |
| Database | PostgreSQL 16 |
| Bot | aiogram 3.x, OpenRouter (free LLM) |
| Frontend | React 18, Vite, Tailwind CSS, Axios |
| DevOps | Docker, Docker Compose, Nginx (multi-stage) |

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/items/{user_id}` | List of items for a user |
| `POST` | `/api/items/` | Add an item `{name, category, user_id}` |
| `PATCH` | `/api/items/{item_id}` | Toggle `is_bought` status |
| `GET` | `/health` | Health check |
