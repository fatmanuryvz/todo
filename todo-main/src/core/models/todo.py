from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    owner_email:  Optional[str] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_email: str
    created_at: datetime

    class Config:
        from_attributes = True
