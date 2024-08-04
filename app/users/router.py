from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_user():
    return {"message": "This will be implemented soon 🚀"}
