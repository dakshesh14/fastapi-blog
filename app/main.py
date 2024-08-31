from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# local imports
from app.blogs import router as blog_router
from app.config import DEBUG
from app.core.exceptions import (
    APIError,
    AuthenticationFailed,
    AuthorizationFailed,
    BadRequest,
    EntityAlreadyExist,
    EntityNotFound,
)
from app.core.middleware.auth_middleware import AuthMiddleware
from app.users import router as user_router

app = FastAPI(title="FastAPI Blogs", debug=DEBUG)

app.add_middleware(AuthMiddleware)

app.include_router(user_router.router, prefix="/api/users", tags=["users"])
app.include_router(blog_router.router, prefix="/api/blogs", tags=["blogs"])


def create_exception_handler(
    status_code: int, initial_detail: str
) -> Callable[[Request, APIError], JSONResponse]:
    detail = {"message": initial_detail}

    async def exception_handler(_: Request, exc: APIError) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message

        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        return JSONResponse(
            status_code=status_code, content={"detail": detail["message"]}
        )

    return exception_handler


app.add_exception_handler(
    exc_class_or_status_code=EntityNotFound,
    handler=create_exception_handler(status.HTTP_404_NOT_FOUND, "Entity not found."),
)


app.add_exception_handler(
    exc_class_or_status_code=AuthenticationFailed,
    handler=create_exception_handler(
        status.HTTP_401_UNAUTHORIZED, "Authentication credential were not provided."
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=AuthorizationFailed,
    handler=create_exception_handler(
        status.HTTP_403_FORBIDDEN, "Authorization failed."
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=EntityAlreadyExist,
    handler=create_exception_handler(
        status.HTTP_409_CONFLICT, "Entity already exists."
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=BadRequest,
    handler=create_exception_handler(status.HTTP_400_BAD_REQUEST, "Bad request."),
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = exc.errors()
    print("errors: ", errors)
    formatted_errors = {str(error["loc"][-1]): [error["msg"]] for error in errors}
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=formatted_errors,
    )
