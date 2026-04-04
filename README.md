# 🛒 Smart Grocery Sync

AI-powered grocery list with smart item parsing and automatic recipe generation.

## Demo

### Web Interface — Shopping List
<img width="1000" height="1280" alt="image" src="https://github.com/user-attachments/assets/b603795b-2154-4f07-9c6d-db95a9cc8c59" />

Items are grouped by category (Vegetables, Fruits, Dairy, etc.) with smooth checkbox animations.

### Recipe Generator
<img width="1000" height="1280" alt="image" src="https://github.com/user-attachments/assets/db3ca732-465a-4c69-9da9-dd44b14f3e46" />

Click "✨ Magic Recipe" and get a unique recipe from items you've already bought.

### Telegram Bot
<img width="669" height="1280" alt="image" src="https://github.com/user-attachments/assets/99034797-11d6-4f90-af34-44b1992a673a" />

Send a natural-language message like "Buy apples, milk, bread" and the AI extracts, categorizes, and saves each item.

---

## Product Context

### End Users
Anyone who shops for groceries — students, families, roommates — and wants to keep track of what to buy and what they already have.

### Problem
People forget what they need to buy, lose paper lists, and don't know what to cook from ingredients they already have at home.

### Our Solution
A smart grocery list that you can manage from a web app or by simply messaging a Telegram bot. Mark items as bought, then let AI invent a recipe from what you have. One sentence to the bot or a click in the web app — that's all it takes.

---

## Features

### Version 1 (Core)
| Feature | Status |
|---|---|
| Add grocery items via web form (name + category) | ✅ Implemented |
| Toggle bought status with checkbox | ✅ Implemented |
| View items grouped by category | ✅ Implemented |
| AI-powered Telegram bot that parses natural language | ✅ Implemented |
| Persistent storage in PostgreSQL | ✅ Implemented |
| REST API (FastAPI + SQLAlchemy async) | ✅ Implemented |
| Docker Compose deployment | ✅ Implemented |

### Version 2 (Extended)
| Feature | Status |
|---|---|
| AI Recipe Generator — generates recipes from bought items | ✅ Implemented |
| `/list` command in Telegram — show current shopping list | ✅ Implemented |
| `/clear` command in Telegram — delete all items | ✅ Implemented |
| Delete individual items from web UI | ✅ Implemented |
| Clear all items button in web UI | ✅ Implemented |
| Animated UI (checkbox bounce, modal transitions) | ✅ Implemented |
| Structured logging in backend and bot | ✅ Implemented |

---

## Usage

### Web App
1. Open `http://<VM_IP>:3000` in your browser
2. Add items manually using the form (name + category)
3. Check off items as you buy them
4. Click **✨ Magic Recipe** to generate a recipe from bought items
5. Click **🗑️ Clear All** to reset the list
6. Hover over an item and click **✕** to delete it individually

### Telegram Bot *(requires Telegram access)*
| Action | Example |
|---|---|
| Add items | `Buy apples, milk, bread and chicken` |
| Show list | `/list` |
| Clear list | `/clear` |
| Generate recipe | `/recipe` |
| Help | `/help` |

### REST API
```bash
# Health check
curl http://localhost:8000/health

# Add an item
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bread", "category": "Grocery", "user_id": 1}'

# Get all items
curl http://localhost:8000/api/items/1

# Toggle bought status
curl -X PATCH http://localhost:8000/api/items/1

# Delete single item
curl -X DELETE http://localhost:8000/api/items/1

# Clear all items
curl -X DELETE http://localhost:8000/api/items/user/1

# Generate recipe from bought items
curl -X POST http://localhost:8000/api/generate-recipe/1
```

---

## Deployment

### Requirements
- **OS**: Ubuntu 24.04 LTS (tested on university VMs)
- **Docker** and **Docker Compose** (step-by-step below)
- **Internet access** for pulling Docker images and calling OpenRouter API
- **Ports**: 3000 (frontend), 8000 (backend API) must be accessible

> **Note**: Telegram bots are blocked on university VMs. The bot works on any unrestricted network. The web app and API are fully functional without Telegram.

### Step-by-Step

#### 1. Install Docker

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
# Re-login for the group change to take effect
```

Verify:
```bash
docker --version
docker compose version
```

#### 2. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/se-toolkit-hackathon.git
cd se-toolkit-hackathon

cp .env.example .env
nano .env
```

Required `.env` variables:

| Variable | Description | Required for |
|---|---|---|
| `OPENROUTER_API_KEY` | Free LLM API key from [openrouter.ai](https://openrouter.ai) | Recipe generation + bot |
| `POSTGRES_PASSWORD` | Database password | All services |
| `TG_BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) | Telegram bot (optional) |

> Get a free `OPENROUTER_API_KEY` at [openrouter.ai/keys](https://openrouter.ai/keys) — no credit card needed.

#### 3. Open Firewall Ports

```bash
sudo ufw allow 3000/tcp    # Frontend
sudo ufw allow 8000/tcp    # Backend API
sudo ufw reload
```

If using a cloud provider (AWS, GCP, etc.), also open these ports in the security group.

#### 4. Launch

```bash
docker compose up -d --build
```

Check that everything started:
```bash
docker compose ps
docker compose logs -f
```

#### 5. Access

| Service | URL |
|---|---|
| Web App | `http://<VM_IP>:3000` |
| API Docs (Swagger) | `http://<VM_IP>:8000/docs` |
| Backend API | `http://<VM_IP>:8000` |

---

## Architecture

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

### Tech Stack

| Component | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (async), asyncpg |
| **Database** | PostgreSQL 16 |
| **Bot** | aiogram 3.x, OpenRouter (free LLM) |
| **Frontend** | React 18, Vite, Tailwind CSS, Axios |
| **DevOps** | Docker, Docker Compose, Nginx (multi-stage build) |

### API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/items/{user_id}` | All items for a user |
| `GET` | `/api/items/{user_id}?is_bought=false` | Only unbought items |
| `POST` | `/api/items/` | Add an item `{name, category, user_id}` |
| `PATCH` | `/api/items/{item_id}` | Toggle `is_bought` status |
| `DELETE` | `/api/items/{item_id}` | Delete a single item |
| `DELETE` | `/api/items/user/{user_id}` | Delete all items for a user |
| `POST` | `/api/generate-recipe/{user_id}` | Generate recipe from bought items |
