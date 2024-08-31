from datetime import datetime
from typing import Optional

from pydantic import BaseModel

# local imports
from app.users.schemas import UserPublic


class BlogCreate(BaseModel):
    title: str
    content: str


class Blog(BaseModel):
    id: str
    title: str
    slug: str
    content: str

    created_at: datetime
    updated_at: datetime

    author_id: str
    author: UserPublic


class PaginatedBlogsResponse(BaseModel):
    results: list[Blog]
    count: int
    next: Optional[str]
    previous: Optional[str]


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
