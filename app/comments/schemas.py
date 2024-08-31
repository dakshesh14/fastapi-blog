from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# local imports
from app.users.schemas import UserPublic


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None


class Comment(BaseModel):
    id: str
    content: str

    actor_id: str
    blog_id: str
    parent_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    actor: UserPublic

    children: List["Comment"] = []


Comment.model_rebuild()


class CommentUpdate(BaseModel):
    content: str
