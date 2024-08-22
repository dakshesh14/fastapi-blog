import uuid

# psycopg2
from psycopg2.errors import UniqueViolation


# local imports
from app.db import get_connection, release_connection
from app.core.string import slugify, random_string
from app.blogs.schemas import BlogCreate, BlogUpdate, Blog
from app.users.services import get_user_by_id


class BlogService:
    @staticmethod
    async def create_blog(user_id: str, data: BlogCreate) -> Blog:
        conn = get_connection()
        try:
            blog_id = str(uuid.uuid4())
            slug = slugify(data.title) + "-" + random_string(6)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO blogs
                    (id, title, slug, content, author_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        blog_id,
                        data.title,
                        slug,
                        data.content,
                        user_id,
                    ),
                )
            return BlogService.get_blog(blog_id)
        except UniqueViolation as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def get_blog(blog_id: str) -> Blog:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT INTO blogs
                    (id, title, slug, content, author_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        blog_id,
                        data.title,
                        slug,
                        data.content,
                        user_id,
                    ),
                )
        except UniqueViolation as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def get_blogs() -> list[Blog]:
        pass

    @staticmethod
    async def update_blog(blog_id: str, blog_update: BlogUpdate) -> Blog:
        pass

    @staticmethod
    async def delete_blog(blog_id: str) -> None:
        pass
