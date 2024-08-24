from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

# local imports
from app.users.schemas import UserPublic


class BlogCreate(BaseModel):
    title: str
    content: str


class Blog(BaseModel):
    id: UUID
    title: str
    slug: str
    content: str

    created_at: datetime
    updated_at: datetime

    author_id: UUID
    author: UserPublic


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
