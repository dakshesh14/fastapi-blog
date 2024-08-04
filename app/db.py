import psycopg2

from app.config import DATABASE_URL

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1, maxconn=10, dsn=DATABASE_URL
)


def get_connection():
    return connection_pool.getconn()


def release_connection(conn):
    connection_pool.putconn(conn)
