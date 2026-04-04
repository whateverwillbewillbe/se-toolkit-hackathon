from pydantic import BaseModel, Field
from typing import Optional


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="Другое", max_length=100)
    user_id: int


class ItemResponse(BaseModel):
    id: int
    name: str
    category: str
    is_bought: bool
    user_id: int

    model_config = {"from_attributes": True}


class ItemUpdate(BaseModel):
    is_bought: Optional[bool] = None
