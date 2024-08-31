from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.comments.authorizer import author_only

# local imports
from app.comments.schemas import CommentCreate, CommentUpdate
from app.comments.services import CommentService
from app.core.auth import get_current_user

router = APIRouter()


@router.post("/{blog_id}")
async def create_comment_api(
    blog_id: str,
    form_data: CommentCreate,
    user=Depends(get_current_user),
):
    try:
        comment = await CommentService.create(
            blog_id=blog_id,
            actor_id=user.id,
            data=form_data,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(comment)
        )
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.args[0])


@router.get("/{comment_id}")
async def get_comment(comment_id: str):
    comment = await CommentService.get_by_id(comment_id)
    return comment


@router.get("/blog/{blog_id}")
async def get_comments_by_blog_id(blog_id: str):
    comments = await CommentService.get_comments_by_blog_id(blog_id)
    return comments


@router.patch("/{comment_id}")
async def update_comment(
    comment_id: str,
    form_data: CommentUpdate,
    _=Depends(get_current_user),
    __=Depends(author_only),
):
    comment = await CommentService.update(comment_id, form_data)
    return comment


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    _=Depends(get_current_user),
    __=Depends(author_only),
):
    await CommentService.delete(comment_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
