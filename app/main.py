from fastapi import FastAPI

from app.users import router as user_router

app = FastAPI()

app.include_router(user_router.router, prefix="/api/users", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI app"}
