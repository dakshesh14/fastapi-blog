from fastapi import Depends, HTTPException, status

# local imports
from app.blogs.services import BlogService
from app.core.auth import get_current_user
from app.users.schemas import User


async def author_only(
    blog_id: str,
    user: User = Depends(get_current_user),
):
    blog = await BlogService.get_by_id(blog_id)

    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    if blog.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have authorization.",
        )

    return blog
