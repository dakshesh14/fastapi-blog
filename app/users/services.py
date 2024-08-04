# uuid
import uuid

# argon
from argon2 import PasswordHasher

# psycopg2
from psycopg2.errors import UniqueViolation

# db
from app.db import get_connection, release_connection

# schemas
from app.users.schemas import User


def create_user(
    email: str,
    username: str,
    password: str,
    first_name: str,
    last_name: str,
):
    conn = get_connection()
    try:
        password_hash = _hash_password(password)
        user_id = str(uuid.uuid4())

        _insert_user(
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
        _handle_unique_violation(e)
    finally:
        release_connection(conn)


def _hash_password(password: str) -> str:
    hasher = PasswordHasher()
    return hasher.hash(password)


def _insert_user(
    conn,
    user_id: str,
    email: str,
    username: str,
    password_hash: str,
    first_name: str,
    last_name: str,
) -> None:
    with conn.cursor() as cur:
        try:
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
        except UniqueViolation as e:
            conn.rollback()
            raise e


def _handle_unique_violation(error: UniqueViolation) -> None:
    if "email" in str(error):
        raise ValueError({"email": ["Email already exists"]})
    elif "username" in str(error):
        raise ValueError({"username": ["Username already exists"]})
    else:
        raise ValueError(
            {"non_field_errors": ["Something went wrong. Please try again later"]}
        )


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
