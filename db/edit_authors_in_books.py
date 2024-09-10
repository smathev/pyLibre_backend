from sqlalchemy.future import select
from db.db_manager.async_db_manager import AsyncDBManager
from db.classDefinitions.book_author_links import BookAuthorLinks
from loguru import logger


class EditAuthorsInBook(AsyncDBManager):
    def __init__(self):
        super().__init__()

    # async def delete_author_from_book(self, book_id, author_id):
    async def delete_author_from_book(self, author_update_schema):
        async with self.get_session() as session:
            try:
                # Correctly querying to find the author-book relationship
                stmt = select(BookAuthorLinks).where(
                    BookAuthorLinks.book_id == author_update_schema.book_id,
                    BookAuthorLinks.author_id == author_update_schema.author_id,
                )
                result = await session.execute(stmt)
                book_author_links = result.scalars().first()

                if not book_author_links:
                    logger.info("No such author associated with this book")
                    return {
                        "status": "error",
                        "message": "No such author associated with this book",
                    }, 404

                # Delete the association
                await session.delete(book_author_links)
                await session.commit()
                logger.info("Author removed from book")
                return {"status": "success", "message": "Author removed from book"}

            except Exception as e:
                logger.error(f"Error while deleting author from book: {e}")
                return {"status": "error", "message": str(e)}, 500
                raise e

    async def add_author_to_book(self, author_update_schema):
        async with self.get_session() as session:  # Ensure you are passing the session correctly
            try:
                # Find the association in the authors_in_books table
                result = await session.execute(
                    select(BookAuthorLinks).filter_by(
                        book_id=author_update_schema.book_id,
                        author_id=author_update_schema.author_id,
                    )
                )
                book_author_link = result.scalars().first()

                if not book_author_link:
                    # Create new association since it doesn't exist
                    new_link = BookAuthorLinks(
                        book_id=author_update_schema.book_id,
                        author_id=author_update_schema.author_id,
                        primary_author=author_update_schema.primary_author,
                    )
                    session.add(new_link)
                    await session.commit()
                    return {"status": "success", "message": "Author added to book"}

                return {
                    "status": "error",
                    "message": "Author already associated with this book",
                }, 400

            except Exception as e:
                logger.error(f"Error adding author to book: {e}")
                await session.rollback()  # Rollback on error
                return {"status": "error", "message": str(e)}, 500

    async def set_primary_author_in_book(self, author_id, book_id):
        async with self.get_session() as session:
            try:
                # Find the book and check if the book has a primary author
                has_primary_author = False
                current_primary_author = 0
                pass
                if has_primary_author:
                    # Set the primary author
                    # remove primary author
                    pass
                else:
                    # set primary author
                    pass

                return {"status": "success", "message": "Author added to book"}

            except Exception as e:
                logger.error(f"Error setting primary author: {e}")
                return {"status": "error", "message": str(e)}, 500
