import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routers import items, recipe

# Configure root-level logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Smart Grocery Sync API v2")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Smart Grocery Sync API",
    description="AI-powered grocery list with recipe generation",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS: allow React dev server on port 5173 and Nginx on port 80
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://frontend:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(recipe.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}
