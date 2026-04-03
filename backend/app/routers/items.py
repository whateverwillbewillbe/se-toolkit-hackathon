from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("/{user_id}", response_model=List[ItemResponse])
async def get_items(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.user_id == user_id).order_by(Item.is_bought, Item.name))
    items = result.scalars().all()
    return items


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item_data: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = Item(
        name=item_data.name,
        category=item_data.category,
        user_id=item_data.user_id,
        is_bought=False,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_bought = not item.is_bought
    await db.commit()
    await db.refresh(item)
    return item
