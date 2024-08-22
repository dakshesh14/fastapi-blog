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

    created_at: str
    updated_at: str

    author_id: str
    author: UserPublic


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
