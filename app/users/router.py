from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# local imports
from app.core.auth import get_current_user
from app.users.schemas import UserCreate, UserLogin, UserUpdate
from app.users.services import UserService

router = APIRouter()


@router.post("/")
async def create_user_api(form_data: UserCreate):
    try:
        user = await UserService.create(
            email=form_data.email,
            username=form_data.username,
            password=form_data.password,
            first_name=form_data.first_name,
            last_name=form_data.last_name,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content=jsonable_encoder(user)
        )
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=e.args[0])


@router.post("/login")
async def login(form_data: UserLogin):
    try:
        response = await UserService.authenticate(
            email=form_data.email,
            password=form_data.password,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(response)
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=e.args[0],
        )


@router.get("/me")
async def get_me(_: Request, user=Depends(get_current_user)):
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(user))


@router.patch("/me")
async def update_me(form_data: UserUpdate, user=Depends(get_current_user)):
    try:
        response = await UserService.update(form_data, user)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(response)
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=e.args[0],
        )
