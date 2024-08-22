import uuid

# psycopg2
from psycopg2.errors import UniqueViolation

# local imports
from app.blogs.schemas import Blog, BlogCreate, BlogUpdate
from app.core.string import random_string, slugify
from app.db import get_connection, release_connection
from app.users.schemas import UserPublic


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
                    SELECT 
                        blogs.id,
                        blogs.title,
                        blogs.slug,
                        blogs.content,
                        blogs.author_id,
                        users.id,
                        users.username,
                        users.created_at,
                        users.updated_at,
                    FROM 
                        blogs
                    JOIN
                        users ON blogs.author_id = users.id
                    WHERE
                        blogs.id = %s
                    """,
                    (blog_id,),
                )
                blog = cur.fetchone()
                if blog is None:
                    # TODO: raise custom exception for entity not found
                    raise Exception("Blog not found")

                return Blog(
                    id=blog[0],
                    title=blog[1],
                    slug=blog[2],
                    content=blog[3],
                    created_at=blog[4],
                    updated_at=blog[5],
                    author_id=blog[6],
                    author=UserPublic(
                        id=blog[7],
                        username=blog[8],
                        created_at=blog[9],
                        updated_at=blog[10],
                    ),
                )

        except UniqueViolation as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def get_blogs() -> list[Blog]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        blogs.id,
                        blogs.title,
                        blogs.slug,
                        blogs.content,
                        blogs.author_id,
                        users.id,
                        users.username,
                        users.created_at,
                        users.updated_at
                    FROM 
                        blogs
                    JOIN
                        users ON blogs.author_id = users.id
                    """
                )
                blogs = cur.fetchall()
                blog_list = []

                for blog in blogs:
                    blog_list.append(
                        Blog(
                            id=blog[0],
                            title=blog[1],
                            slug=blog[2],
                            content=blog[3],
                            created_at=blog[4],
                            updated_at=blog[5],
                            author_id=blog[6],
                            author=UserPublic(
                                id=blog[7],
                                username=blog[8],
                                created_at=blog[9],
                                updated_at=blog[10],
                            ),
                        )
                    )

        finally:
            release_connection(conn)

        return blog_list

    @staticmethod
    async def update_blog(blog_id: str, blog_update: BlogUpdate) -> Blog:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE blogs
                        title = %s,
                        content = %s
                    WHERE
                        id = %s
                    """,
                    (
                        blog_update.title,
                        blog_update.content,
                        blog_id,
                    ),
                )
                conn.commit()
                return BlogService.get_blog(blog_id)

        finally:
            release_connection(conn)

    @staticmethod
    async def delete_blog(blog_id: str) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE blogs 
                    WHERE 
                        blogs.id = %s
                    """,
                    (blog_id,),
                )
                conn.commit()
        finally:
            release_connection(conn)
