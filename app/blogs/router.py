from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

# local imports
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
    return JSONResponse(status_code=status.HTTP_200_OK, content=blogs)


@router.post("/")
def create_blog_api(
    form_data: BlogCreate,
    user=Depends(get_current_user),
):
    try:
        blog = BlogService.create_blog(
            user_id=user.id,
            data=form_data,
        )
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=blog)
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.args[0])


@router.get("/{blog_id}")
def get_blog(blog_id: str):
    blog = BlogService.get_blog(blog_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=blog)


# TODO: add authorisation
@router.patch("/{blog_id}")
def update_blog(
    blog_id: str,
    form_data: BlogUpdate,
    _=Depends(get_current_user),
):
    blog = BlogService.update_blog(blog_id, form_data)
    return JSONResponse(status_code=status.HTTP_200_OK, content=blog)


# TODO: add authorisation
@router.delete("/{blog_id}")
def delete_blog(
    blog_id: str,
    _=Depends(get_current_user),
):
    BlogService.delete_blog(blog_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
