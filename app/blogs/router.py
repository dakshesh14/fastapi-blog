from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# local imports
from app.blogs.authorizer import author_only
from app.blogs.schemas import BlogCreate, BlogUpdate
from app.blogs.services import BlogService
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_blogs():
    """
    Get all blogs.
    """
    blogs = await BlogService.get_blogs()
    return blogs


@router.post("/")
async def create_blog_api(
    form_data: BlogCreate,
    user=Depends(get_current_user),
):
    try:
        blog = await BlogService.create(
            user_id=user.id,
            data=form_data,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(blog)
        )
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.args[0])


@router.get("/{blog_id}")
async def get_blog(blog_id: str):
    blog = await BlogService.get_by_id(blog_id)
    return blog


@router.patch("/{blog_id}")
async def update_blog(
    blog_id: str,
    form_data: BlogUpdate,
    _=Depends(get_current_user),
    __=Depends(author_only),
):
    blog = await BlogService.update(blog_id, form_data)
    return blog


@router.delete("/{blog_id}")
async def delete_blog(
    blog_id: str,
    _=Depends(get_current_user),
    __=Depends(author_only),
):
    await BlogService.delete(blog_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
