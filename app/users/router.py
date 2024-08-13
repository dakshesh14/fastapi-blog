from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

# local imports
from app.core.auth import get_current_user
from app.users.schemas import UserCreate, UserLogin, UserUpdate
from app.users.services import authenticate, create_user, get_user_by_id, update_user

router = APIRouter()


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


@router.get("/me")
def get_me(request: Request, user=Depends(get_current_user)):
    return user


@router.patch("/me")
def update_me(form_data: UserUpdate, user=Depends(get_current_user)):
    return update_user(form_data, user)
