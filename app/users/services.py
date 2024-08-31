import uuid
from datetime import datetime, timedelta, timezone

import jwt
from psycopg2.errors import UniqueViolation

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.db import get_connection, release_connection
from app.users.helpers import handle_unique_violation, hash_password, verify_password
from app.users.schemas import LoginResponse, User, UserUpdate


class UserService:
    @staticmethod
    async def create(
        email: str,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> str:
        conn = get_connection()
        try:
            password_hash = hash_password(password)
            user_id = str(uuid.uuid4())

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users
                    (id, email, username, password, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        email,
                        username,
                        password_hash,
                        first_name,
                        last_name,
                    ),
                )
                conn.commit()

            return await UserService.get_by_id(user_id)
        except UniqueViolation as e:
            conn.rollback()
            handle_unique_violation(e)
        finally:
            release_connection(conn)

    @staticmethod
    async def get_by_id(user_id: str) -> User:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, username,
                    first_name, last_name, created_at,
                    updated_at FROM users WHERE id = %s
                    """,
                    (user_id,),
                )
                user = cur.fetchone()
                user = User(
                    id=user[0],
                    email=user[1],
                    username=user[2],
                    first_name=user[3],
                    last_name=user[4],
                    created_at=user[5].isoformat(),
                    updated_at=user[6].isoformat(),
                )
        finally:
            release_connection(conn)

        return user

    @staticmethod
    async def get_by_token(token: str) -> User:
        token = token.replace("Bearer ", "")

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = await UserService.get_by_id(payload.get("id"))
            return user
        except Exception as e:
            print(e)
            raise ValueError(
                {
                    "non_field_errors": [
                        "Could not validate credentials",
                    ]
                }
            ) from e

    @staticmethod
    async def update(form_data: UserUpdate, user: User) -> User:
        email = form_data.email if form_data.email is not None else user.email
        username = (
            form_data.username if form_data.username is not None else user.username
        )
        first_name = (
            form_data.first_name
            if form_data.first_name is not None
            else user.first_name
        )
        last_name = (
            form_data.last_name if form_data.last_name is not None else user.last_name
        )

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET email = %s,
                        username = %s,
                        first_name = %s,
                        last_name = %s
                    WHERE id = %s
                    """,
                    (
                        email,
                        username,
                        first_name,
                        last_name,
                        user.id,
                    ),
                )
                conn.commit()

            return await UserService.get_by_id(user.id)

        except ValueError as e:
            print(e)
            conn.rollback()
            raise e

        except Exception as e:
            print(e)
            conn.rollback()
            raise ValueError(
                {
                    "non_field_errors": [
                        "Something went wrong. Please try again later",
                    ]
                }
            ) from e
        finally:
            release_connection(conn)

    @staticmethod
    async def authenticate(email: str, password: str) -> LoginResponse:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, password
                    FROM users
                    WHERE email = %s
                    """,
                    (email,),
                )
                user = cur.fetchone()
                if not user or not verify_password(password, user[1]):
                    raise ValueError(
                        {
                            "non_field_errors": [
                                "Invalid email or password",
                            ]
                        }
                    )

            user = await UserService.get_by_id(user[0])

            token_expiration = int(
                (datetime.now(timezone.utc) + timedelta(days=1)).timestamp()
            )

            user_dict = UserService.serializer_user(user)

            token = jwt.encode(
                {**user_dict, "exp": token_expiration},
                JWT_SECRET_KEY,
                algorithm=JWT_ALGORITHM,
                headers={"exp": token_expiration},
            )

            return LoginResponse(token=token, user=user)

        except ValueError as e:
            raise e

        except Exception as e:
            print(e)
            raise ValueError(
                {
                    "non_field_errors": [
                        "Something went wrong. Please try again later",
                    ]
                }
            ) from e
        finally:
            release_connection(conn)

    @staticmethod
    def serializer_user(user: User) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
