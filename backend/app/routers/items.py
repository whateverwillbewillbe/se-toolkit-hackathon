from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("/{user_id}", response_model=List[ItemResponse])
async def get_items(user_id: int, is_bought: Optional[bool] = None, db: AsyncSession = Depends(get_db)):
    query = select(Item).where(Item.user_id == user_id)
    if is_bought is not None:
        query = query.where(Item.is_bought == is_bought)
    query = query.order_by(Item.category, Item.name)
    result = await db.execute(query)
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


@router.delete("/{user_id}", status_code=200)
async def delete_items(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete all items for a user."""
    result = await db.execute(delete(Item).where(Item.user_id == user_id))
    await db.commit()
    deleted_count = result.rowcount
    return {"message": f"Deleted {deleted_count} items", "deleted_count": deleted_count}
