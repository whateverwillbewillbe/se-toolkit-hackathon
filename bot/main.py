import os
import logging
import json
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from openai import AsyncOpenAI
from pydantic_settings import BaseSettings

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    TG_BOT_TOKEN: str
    OPENROUTER_API_KEY: str
    BACKEND_URL: str = "http://backend:8000"
    LLM_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"

    class Config:
        env_file = ".env"


settings = Settings()

bot = Bot(token=settings.TG_BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

VALID_CATEGORIES = ["Овощи", "Фрукты", "Молочка", "Мясо", "Бакалея", "Другое"]

SYSTEM_PROMPT = (
    "Ты — ассистент по покупкам. Извлеки список продуктов из сообщения пользователя "
    "и верни ТОЛЬКО валидный JSON массив объектов без какого-либо дополнительного текста. "
    "Формат: [{\"name\": \"...\", \"category\": \"...\"}]. "
    f"Категории выбери ТОЛЬКО из: {', '.join(VALID_CATEGORIES)}. "
    "Если категория неочевидна, используй 'Другое'. "
    "Не добавляй markdown-блоки, не добавляй пояснений. Только JSON."
)


def _parse_json_from_response(text: str) -> list:
    """Extract JSON array from LLM response, handling possible markdown fences."""
    cleaned = text.strip()
    # Remove markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    # Try to find JSON array in text
    match = re.search(r"\[[\s\S]*\]", cleaned)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return []


async def send_to_backend(items: list, user_id: int) -> int:
    """Send parsed items to the backend API. Returns count of saved items."""
    saved = 0
    async with aiohttp.ClientSession() as session:
        for item in items:
            name = item.get("name", "").strip()
            category = item.get("category", "Другое")
            if category not in VALID_CATEGORIES:
                category = "Другое"
            if not name:
                continue
            payload = {"name": name, "category": category, "user_id": user_id}
            try:
                async with session.post(
                    f"{settings.BACKEND_URL}/api/items/",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as resp:
                    if resp.status in (200, 201):
                        saved += 1
                    else:
                        logger.warning(f"Failed to save '{name}': status {resp.status}")
            except aiohttp.ClientError as e:
                logger.error(f"Connection error saving '{name}': {e}")
    return saved


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я — бот для списка покупок.\n"
        "Напиши мне, что нужно купить (например: *Купи яблоки и молоко*), "
        "и я добавлю это в твой список.\n\n"
        "Также можно управлять списком через веб-приложение."
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Просто напиши список покупок в любом формате.\n"
        "Пример: `Купи 2 яблока, молоко, хлеб и курицу`\n"
        "Я распознаю продукты и распределю по категориям."
    )


@dp.message()
async def handle_grocery_list(message: types.Message):
    user_id = message.from_user.id

    # Typing indicator
    await bot.send_chat_action(chat_id=user_id, action="typing")

    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text},
            ],
            temperature=0.1,
            max_tokens=500,
        )
        raw_text = response.choices[0].message.content or "[]"
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        await message.answer("Произошла ошибка при обработке запроса. Попробуйте позже.")
        return

    items = _parse_json_from_response(raw_text)

    if not items:
        await message.answer(
            "Не удалось распознать продукты. Попробуйте переформулировать запрос.\n"
            "Пример: `Купи яблоки, молоко, хлеб`"
        )
        return

    saved_count = await send_to_backend(items, user_id)

    items_list = "\n".join(f"• {it.get('name', '?')} ({it.get('category', 'Другое')})" for it in items)

    await message.answer(
        f"Добавлено в список ({saved_count} шт.):\n{items_list}",
        parse_mode=None,
    )


async def main():
    logger.info("Starting grocery bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
