import uuid

# local imports
from app.comments.schemas import Comment, CommentCreate, CommentUpdate
from app.db import get_connection, release_connection
from app.users.schemas import UserPublic


class CommentService:
    @staticmethod
    async def create(
        blog_id: str,
        actor_id: str,
        data: CommentCreate,
    ) -> Comment:
        conn = get_connection()
        try:
            comment_id = str(uuid.uuid4())

            with conn.cursor() as cur:
                cur.execute(
                    """
                INSERT INTO comments
                (id, content, blog_id, actor_id, parent_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        comment_id,
                        data.content,
                        blog_id,
                        actor_id,
                        data.parent_id,
                    ),
                )
                conn.commit()
            return await CommentService.get_by_id(comment_id)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def update(comment_id: str, data: CommentUpdate) -> Comment:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE comments
                    SET
                        content = %s
                    WHERE
                        id = %s
                    """,
                    (
                        data.content,
                        comment_id,
                    ),
                )
                conn.commit()
            return await CommentService.get_by_id(comment_id)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def get_by_id(comment_id: str) -> Comment:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        comment.id,
                        comment.content,
                        comment.actor_id,
                        comment.blog_id,
                        comment.parent_id,
                        comment.created_at,
                        comment.updated_at,
                        actor.id,
                        actor.username,
                        actor.created_at,
                        actor.updated_at
                    FROM
                        comments comment
                    JOIN
                        users actor on comment.actor_id = actor.id
                    WHERE
                        comment.id = %s
                    """,
                    (comment_id,),
                )
                comment = cur.fetchone()

                return Comment(
                    id=comment[0],
                    content=comment[1],
                    actor_id=comment[2],
                    blog_id=comment[3],
                    parent_id=comment[4],
                    created_at=comment[5],
                    updated_at=comment[6],
                    actor=UserPublic(
                        id=comment[7],
                        username=comment[8],
                        created_at=comment[9],
                        updated_at=comment[10],
                    ),
                )
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def get_comments_by_blog_id(blog_id: str) -> list[Comment]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH RECURSIVE comment_tree AS (
                        SELECT
                            comment.id AS comment_id,
                            comment.content,
                            comment.actor_id,
                            comment.blog_id,
                            comment.parent_id,
                            comment.created_at,
                            comment.updated_at,
                            actor.id,
                            actor.username,
                            actor.created_at,
                            actor.updated_at,
                            0 AS level
                        FROM
                            comments comment
                        JOIN
                            users actor ON comment.actor_id = actor.id
                        WHERE
                            comment.blog_id = %s
                        UNION ALL
                        SELECT
                            comment.id,
                            comment.content,
                            comment.actor_id,
                            comment.blog_id,
                            comment.parent_id,
                            comment.created_at,
                            comment.updated_at,
                            actor.id,
                            actor.username,
                            actor.created_at,
                            actor.updated_at,
                            level + 1
                        FROM
                            comments comment
                        JOIN
                            users actor ON comment.actor_id = actor.id
                        JOIN
                            comment_tree ON comment.parent_id = comment_tree.comment_id
                    )
                    SELECT * FROM comment_tree
                    """,
                    (blog_id,),
                )
                comments = cur.fetchall()

            # Process comments into a hierarchy
            comment_dict = {}
            for row in comments:
                comment = Comment(
                    id=row[0],
                    content=row[1],
                    actor_id=row[2],
                    blog_id=row[3],
                    parent_id=row[4],
                    created_at=row[5],
                    updated_at=row[6],
                    actor=UserPublic(
                        id=row[7],
                        username=row[8],
                        created_at=row[9],
                        updated_at=row[10],
                    ),
                )
                comment_dict[comment.id] = comment

            # Build hierarchy
            for comment in comment_dict.values():
                parent_id = comment.parent_id
                if parent_id in comment_dict:
                    parent_comment = comment_dict[parent_id]
                    if not hasattr(parent_comment, "children"):
                        parent_comment.children = []
                    parent_comment.children.append(comment)

            # Return top-level comments
            return [
                comment
                for comment in comment_dict.values()
                if comment.parent_id is None
            ]

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)

    @staticmethod
    async def delete(comment_id: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM comments
                    WHERE
                        id = %s
                    """,
                    (comment_id,),
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            release_connection(conn)
