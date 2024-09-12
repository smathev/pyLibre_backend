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
            
    async def set_primary_author_in_book(self, author_update_schema):
        async with self.get_session() as session:
            try:
                # Extract book_id and author_id from the schema
                book_id = author_update_schema.book_id
                author_id = author_update_schema.author_id

                # Check if there is a primary author for the book
                current_primary_author = await session.execute(
                    select(BookAuthorLinks)
                    .filter_by(book_id=book_id, primary_author=1)
                )
                current_primary_author = current_primary_author.scalars().first()

                # If there is a current primary author, unset them
                if current_primary_author:
                    current_primary_author.primary_author = 0
                    await session.commit()

                # Now set the new author as the primary author
                new_primary_author_link = await session.execute(
                    select(BookAuthorLinks)
                    .filter_by(book_id=book_id, author_id=author_id)
                )
                new_primary_author_link = new_primary_author_link.scalars().first()

                # If the author is already linked to the book, update the primary flag
                if new_primary_author_link:
                    new_primary_author_link.primary_author = 1
                else:
                    # If the author is not yet linked to the book, create a new link
                    new_primary_author_link = BookAuthorLinks(
                        book_id=book_id,
                        author_id=author_id,
                        primary_author=1
                    )
                    session.add(new_primary_author_link)

                # Commit the changes
                await session.commit()

                return {"status": "success", "message": "Primary author changed successfully"}

            except Exception as e:
                await session.rollback()  # Rollback if there's an error
                logger.error(f"Error changing primary author: {e}")
                return {"status": "error", "message": str(e)}

