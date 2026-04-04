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
    LLM_MODEL: str = "qwen/qwen3.6-plus:free"
    DEFAULT_USER_ID: int = 1

    class Config:
        env_file = ".env"


settings = Settings()

bot = Bot(token=settings.TG_BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

VALID_CATEGORIES = ["Vegetables", "Fruits", "Dairy", "Meat", "Grocery", "Other"]

SYSTEM_PROMPT = (
    "You are a shopping assistant. Extract a list of grocery items from the user's message "
    "and return ONLY a valid JSON array of objects, with no additional text. "
    "Format: [{\"name\": \"...\", \"category\": \"...\"}]. "
    f"Choose categories ONLY from: {', '.join(VALID_CATEGORIES)}. "
    "If the category is unclear, use 'Other'. "
    "Do not include markdown code blocks or explanations. Only JSON."
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
            category = item.get("category", "Other")
            if category not in VALID_CATEGORIES:
                category = "Other"
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
        "Hi! I'm your grocery shopping assistant.\n"
        "Tell me what you need to buy (e.g. *Buy apples and milk*), "
        "and I'll add it to your list.\n\n"
        "You can also manage your list via the web app."
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Just write your shopping list in any format.\n"
        "Example: `Get 2 apples, milk, bread, and chicken`\n"
        "I'll recognize the items and categorize them."
    )


@dp.message()
async def handle_grocery_list(message: types.Message):
    chat_id = message.chat.id
    user_id = settings.DEFAULT_USER_ID

    # Typing indicator
    await bot.send_chat_action(chat_id=chat_id, action="typing")

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
        logger.error(f"OpenRouter API error: {e}")
        await message.answer("An error occurred while processing your request. Please try again later.")
        return

    items = _parse_json_from_response(raw_text)

    if not items:
        await message.answer(
            "Couldn't recognize the items. Please try rephrasing your request.\n"
            "Example: `Buy apples, milk, bread`"
        )
        return

    saved_count = await send_to_backend(items, user_id)

    items_list = "\n".join(f"• {it.get('name', '?')} ({it.get('category', 'Other')})" for it in items)

    await message.answer(
        f"Added to your list ({saved_count} items):\n{items_list}",
        parse_mode=None,
    )


async def main():
    logger.info("Starting grocery bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
