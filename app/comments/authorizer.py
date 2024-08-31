from fastapi import Depends, HTTPException, status

# local imports
from app.comments.services import CommentService
from app.core.auth import get_current_user
from app.users.schemas import User


async def author_only(
    comment_id: str,
    user: User = Depends(get_current_user),
):
    comment = await CommentService.get_by_id(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.actor_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have authorization.",
        )

    return comment
