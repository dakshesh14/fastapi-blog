from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# local imports
from app.users.services import UserService


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")

        if token:
            try:
                user = await UserService.get_by_token(token)
                if user:
                    request.state.user = user
            except ValueError as e:
                return JSONResponse(status_code=401, content=e.args[0])
            except Exception as e:
                print(e)
                return JSONResponse(
                    status_code=500, content={"error": "Internal server error"}
                )

        response = await call_next(request)
        return response
