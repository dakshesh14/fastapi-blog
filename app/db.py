from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
from psycopg2 import pool  # NOQA: F401

from app.config import DATABASE_URL

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1, maxconn=10, dsn=DATABASE_URL
)


def get_connection() -> psycopg2.extensions.connection:
    """
    Get a connection from the connection pool.
    """
    conn = connection_pool.getconn()
    print(f"\n\033[34m{get_connection.__name__}: Acquired connection {conn}\033[0m\n")
    return conn


def release_connection(conn: psycopg2.extensions.connection) -> None:
    """
    Release a connection back to the connection pool.
    """
    connection_pool.putconn(conn)
    print(
        f"\n\033[34m{release_connection.__name__}: Released connection {conn}\033[0m\n"
    )
