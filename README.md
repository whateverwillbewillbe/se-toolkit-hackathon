# 🛒 Smart Grocery Sync v2

AI-powered grocery list with Telegram bot, recipe generation, and a modern React interface.

## ✨ Features

- **Smart Parsing** — send any shopping list to the Telegram bot, AI extracts and categorizes items
- **Recipe Generator** — mark items as bought, then generate recipes from what you have
- **Web Interface** — manage your list with a clean, grouped, animated UI
- **Telegram Commands** — `/list`, `/clear`, `/recipe` right in your bot

## 🏗️ Architecture

```
┌─────────────┐    POST /api/items       ┌──────────┐
│  Telegram   │ ──────────────────────►   │          │
│  Bot        │                           │ Backend  │
│  aiogram    │ ◄──────────────────────  │ FastAPI  │
└─────────────┘    GET/PATCH/DELETE       │          │
                                          └────┬─────┘
┌─────────────┐                                │
│  Frontend   │ ◄──────────────────────────────┤
│  React+Vite │                                │
│  Tailwind   │                       ┌────────▼───────┐
└─────────────┘                       │   PostgreSQL   │
                                      └────────────────┘
```

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py            # Entry point, CORS, lifespan
│   │   ├── config.py          # Settings from .env
│   │   ├── database.py        # Async engine, session
│   │   ├── models/item.py     # SQLAlchemy model
│   │   ├── schemas/item.py    # Pydantic DTOs
│   │   └── routers/
│   │       ├── items.py       # CRUD: GET, POST, PATCH, DELETE
│   │       └── recipe.py      # POST /api/generate-recipe
│   ├── requirements.txt
│   └── Dockerfile
├── bot/
│   ├── main.py                # aiogram bot + LLM parsing
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main component (grouped list + recipe modal)
│   │   ├── App.css            # Animations
│   │   ├── api.js             # Axios API client
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf
│   ├── Dockerfile             # Multi-stage: node → nginx
│   └── postcss.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and provide:

| Variable | Description | Where to get |
|---|---|---|
| `TG_BOT_TOKEN` | Telegram bot token | [@BotFather](https://t.me/BotFather) |
| `OPENROUTER_API_KEY` | LLM API key | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `POSTGRES_PASSWORD` | Database password | Your choice |

### 2. Run Everything

```bash
docker compose up --build
```

### 3. Access

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

---

## 🛠️ Deploy on Ubuntu 24.04 VM

### Step 1 — Install Docker

```bash
# Remove old packages
sudo apt remove -y docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable & start
sudo systemctl enable docker
sudo systemctl start docker

# Add your user to docker group (no sudo needed)
sudo usermod -aG docker $USER
```

Verify:
```bash
docker --version
docker compose version
```

### Step 2 — Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/se-toolkit-hackathon.git
cd se-toolkit-hackathon

cp .env.example .env
nano .env  # Fill in TG_BOT_TOKEN, OPENROUTER_API_KEY, POSTGRES_PASSWORD
```

### Step 3 — Open Firewall Ports

```bash
# If UFW is enabled
sudo ufw allow 3000/tcp   # Frontend
sudo ufw allow 8000/tcp   # Backend API
sudo ufw reload

# If using cloud provider (AWS/GCP/etc.), also open ports in the security group
```

### Step 4 — Launch

```bash
docker compose up -d --build

# Check logs
docker compose logs -f

# Check status
docker compose ps
```

### Step 5 — Access from Your Computer

In your browser, open: `http://<VM_IP_ADDRESS>:3000`

---

## 📱 Usage

### Telegram Bot

| Command | Description |
|---|---|
| *Any text* | `Buy apples, milk, bread and chicken` — AI parses and adds items |
| `/list` | Show current shopping list grouped by category |
| `/clear` | Delete all items from your list |
| `/recipe` | Generate a recipe from items marked as bought ✅ |
| `/help` | Show available commands |

### Web Interface

1. **Add items** — type a name, pick a category, click "Add"
2. **Check off items** — click the checkbox (with bounce animation)
3. **Generate recipe** — click "✨ Magic Recipe" to get a recipe from bought items
4. **Clear all** — click "🗑️ Clear All" to reset your list

### API

```bash
# Health check
curl http://localhost:8000/health

# Get all items for user 1
curl http://localhost:8000/api/items/1

# Get only unbought items
curl http://localhost:8000/api/items/1?is_bought=false

# Add an item
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bread", "category": "Grocery", "user_id": 1}'

# Toggle bought status
curl -X PATCH http://localhost:8000/api/items/1

# Delete all items for user 1
curl -X DELETE http://localhost:8000/api/items/1

# Generate recipe from bought items
curl -X POST http://localhost:8000/api/generate-recipe/1
```

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (async), asyncpg |
| **Database** | PostgreSQL 16 |
| **Bot** | aiogram 3.x, OpenRouter (free LLM) |
| **Frontend** | React 18, Vite, Tailwind CSS, Axios |
| **DevOps** | Docker, Docker Compose, Nginx (multi-stage build) |

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/items/{user_id}` | All items for a user |
| `GET` | `/api/items/{user_id}?is_bought=false` | Only unbought items |
| `POST` | `/api/items/` | Add an item `{name, category, user_id}` |
| `PATCH` | `/api/items/{item_id}` | Toggle `is_bought` status |
| `DELETE` | `/api/items/{user_id}` | Delete all items for a user |
| `POST` | `/api/generate-recipe/{user_id}` | Generate recipe from bought items |
