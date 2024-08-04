# argon
from argon2 import PasswordHasher

# psycopg2
from psycopg2.errors import UniqueViolation


def hash_password(password: str) -> str:
    hasher = PasswordHasher()
    return hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    hasher = PasswordHasher()
    try:
        hasher.verify(password_hash, password)
        return True
    except Exception:
        return False


def insert_user(
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


def handle_unique_violation(error: UniqueViolation) -> None:
    if "email" in str(error):
        raise ValueError({"email": ["Email already exists"]})
    elif "username" in str(error):
        raise ValueError({"username": ["Username already exists"]})
    else:
        raise ValueError(
            {"non_field_errors": ["Something went wrong. Please try again later"]}
        )
