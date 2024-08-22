from fastapi import FastAPI

# local imports
from app.blogs import router as blog_router
from app.core.middleware.auth_middleware import AuthMiddleware
from app.users import router as user_router

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(user_router.router, prefix="/api/users", tags=["users"])
app.include_router(blog_router.router, prefix="/api/blogs", tags=["blogs"])


@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI app"}
