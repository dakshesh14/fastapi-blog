import uuid
from datetime import datetime, timedelta, timezone

# jwt
import jwt

# psycopg2
from psycopg2.errors import UniqueViolation

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.db import get_connection, release_connection
from app.users.helpers import (
    handle_unique_violation,
    hash_password,
    insert_user,
    verify_password,
)

# local imports
from app.users.schemas import LoginResponse, User


def create_user(
    email: str,
    username: str,
    password: str,
    first_name: str,
    last_name: str,
):
    conn = get_connection()
    try:
        password_hash = hash_password(password)
        user_id = str(uuid.uuid4())

        insert_user(
            conn,
            user_id,
            email,
            username,
            password_hash,
            first_name,
            last_name,
        )

        return user_id
    except UniqueViolation as e:
        handle_unique_violation(e)
    finally:
        release_connection(conn)


def get_user_by_id(user_id: str) -> User:
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


def get_user_by_token(token: str) -> User:
    token = token.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user = get_user_by_id(payload.get("id"))
        return user
    except Exception as e:
        print(e)
        raise ValueError(
            {
                "non_field_errors": [
                    "Could not validate credentials",
                ]
            }
        )


def authenticate(
    email: str,
    password: str,
):
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

        user = get_user_by_id(user[0])

        token_expiration = int(
            (datetime.now(timezone.utc) + timedelta(days=1)).timestamp()
        )

        token = jwt.encode(
            {**user.model_dump(), "exp": token_expiration},
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
        )
    finally:
        release_connection(conn)
