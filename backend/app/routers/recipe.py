import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.item import Item

logger = logging.getLogger("recipe_generator")

router = APIRouter(prefix="/api/generate-recipe", tags=["recipe"])


@router.post("/{user_id}")
async def generate_recipe(user_id: int, db: AsyncSession = Depends(get_db)):
    """Generate a recipe from bought items."""
    result = await db.execute(
        select(Item)
        .where(Item.user_id == user_id, Item.is_bought == True)
        .order_by(Item.name)
    )
    bought_items = result.scalars().all()

    if not bought_items:
        raise HTTPException(
            status_code=400,
            detail="No bought items found to generate a recipe from.",
        )

    ingredients = ", ".join(item.name for item in bought_items)

    system_prompt = (
        "You are a creative chef. Given a list of available ingredients, "
        "create exactly ONE short, delicious recipe. "
        "Return ONLY valid JSON with no additional text or markdown. "
        "Format: {\"name\": \"Recipe Name\", \"steps\": [\"Step 1\", \"Step 2\", \"Step 3\", \"Step 4\"]}. "
        "Keep it to 3-4 concise steps."
    )

    try:
        from openai import AsyncOpenAI

        openai_client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        response = await openai_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Invent 1 recipe using these ingredients: {ingredients}"},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        raw_text = response.choices[0].message.content or "{}"
        logger.info(f"LLM response for user {user_id}: {raw_text[:200]}")

        import json, re

        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        recipe = json.loads(cleaned)

        return recipe

    except Exception as e:
        logger.error(f"Recipe generation failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recipe: {str(e)}",
        )
