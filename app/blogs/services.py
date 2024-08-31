import uuid

# psycopg2
from psycopg2.errors import UniqueViolation

# local imports
from app.blogs.schemas import Blog, BlogCreate, BlogUpdate, PaginatedBlogsResponse
from app.core.exceptions import EntityNotFound
from app.core.string import random_string, slugify
from app.db import get_connection, release_connection
from app.users.schemas import UserPublic


class BlogService:
    @staticmethod
    async def create(user_id: str, data: BlogCreate) -> Blog:
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
                conn.commit()
            return await BlogService.get_by_id(blog_id)
        except UniqueViolation as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def get_by_id(blog_id: str) -> Blog:
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
                        blogs.created_at,
                        blogs.updated_at,
                        blogs.author_id,
                        users.id,
                        users.username,
                        users.created_at,
                        users.updated_at
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
                    raise EntityNotFound(
                        name="Blogs", message=f"No blog can be found with id: {blog_id}"
                    )

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
                        blog.id,
                        blog.title,
                        blog.slug,
                        blog.content,
                        blog.created_at,
                        blog.updated_at,
                        blog.author_id,
                        author.id,
                        author.username,
                        author.created_at,
                        author.updated_at
                    FROM
                        blogs blog
                    JOIN
                        users author ON blog.author_id = author.id
                    """
                )
                blogs = cur.fetchall()

                return [
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
                    for blog in blogs
                ]

        finally:
            release_connection(conn)

    @staticmethod
    async def get_blogs_paginated(skip: int, limit: int = 20) -> list[Blog]:
        conn = get_connection()
        try:
            offset = skip * limit
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        blog.id,
                        blog.title,
                        blog.slug,
                        blog.content,
                        blog.created_at,
                        blog.updated_at,
                        blog.author_id,
                        author.id,
                        author.username,
                        author.created_at,
                        author.updated_at
                    FROM
                        blogs blog
                    JOIN
                        users author on blog.author_id = author.id
                    ORDER BY blog.created_at DESC
                    LIMIT %s
                    OFFSET %s;
                    """,
                    (
                        limit,
                        offset,
                    ),
                )
                blogs = cur.fetchall()

                cur.execute("SELECT COUNT(*) from blogs")
                total_count = cur.fetchone()[0]

                base_url = "/blogs/"
                next_page = (
                    base_url + f"?skip={skip + 1}&limit={limit}"
                    if (skip + 1) * limit < total_count
                    else None
                )
                prev_page = (
                    base_url + f"?skip={max(skip - 1, 0)}&limit={limit}"
                    if skip > 0
                    else None
                )

                return PaginatedBlogsResponse(
                    count=total_count,
                    next=next_page,
                    previous=prev_page,
                    results=[
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
                        for blog in blogs
                    ],
                )
        finally:
            release_connection(conn)

    @staticmethod
    async def update(blog_id: str, blog_update: BlogUpdate) -> Blog:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE blogs
                    SET
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
                return await BlogService.get_by_id(blog_id)

        finally:
            release_connection(conn)

    @staticmethod
    async def delete(blog_id: str) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM blogs
                    WHERE
                        blogs.id = %s
                    """,
                    (blog_id,),
                )
                conn.commit()
        finally:
            release_connection(conn)
