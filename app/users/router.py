from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

# schemas
from app.users.schemas import UserCreate, UserLogin

# services
from app.users.services import authenticate, create_user, get_user_by_id

router = APIRouter()


@router.get("/")
def get_user():
    return {"message": "This will be implemented soon 🚀"}


@router.post("/")
def create_user_api(form_data: UserCreate):
    try:
        user_id = create_user(
            email=form_data.email,
            username=form_data.username,
            password=form_data.password,
            first_name=form_data.first_name,
            last_name=form_data.last_name,
        )
        user = get_user_by_id(user_id)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=user)
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.args[0])


@router.post("/login")
def login(form_data: UserLogin):
    try:
        response = authenticate(
            email=form_data.email,
            password=form_data.password,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=response.model_dump()
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=e.args[0],
        )
