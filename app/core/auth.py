from fastapi import HTTPException, Request

# local imports
from app.users.schemas import User
from app.users.services import UserService


async def get_current_user(request: Request) -> User:
    """
    A helper function useful to make a route authenticated route.
    If the user is not authenticated, it raises an 401 HTTPException.
    """
    token = request.headers.get("Authorization")

    if token is None:
        raise HTTPException(
            status_code=401, detail="Authentication credentials were not provided."
        )

    try:
        user = await UserService.get_by_token(token)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0]) from e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error") from e
