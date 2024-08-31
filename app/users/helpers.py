# argon
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError

# psycopg2
from psycopg2.errors import UniqueViolation


def hash_password(password: str) -> str:
    hasher = PasswordHasher()
    return hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    hasher = PasswordHasher()
    try:
        return hasher.verify(password_hash, password)
    except (InvalidHash, VerificationError):
        return False


def handle_unique_violation(error: UniqueViolation) -> None:
    if "email" in str(error):
        raise ValueError({"email": ["Email already exists"]})
    elif "username" in str(error):
        raise ValueError({"username": ["Username already exists"]})
    else:
        raise ValueError(
            {"non_field_errors": ["Something went wrong. Please try again later"]}
        )
