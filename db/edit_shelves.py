import uuid
from db.db_manager.sync_db_manager import SyncDBManager
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from db.db_sync_methods import UpdateBookSyncStatus
from db.classDefinitions.book_shelf_links import BookShelfLinks
from db.classDefinitions.shelf import Shelf
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

class CreateNewShelf(SyncDBManager):
    def __init__(self):
        super().__init__()

    def create_new_shelf(self, shelf_name):
        try:
            with self.Session() as session:
                # Check if the shelf already exists in the database
                existing_shelf = session.query(Shelf).filter_by(shelf_name=shelf_name).first()

                if existing_shelf:
                    logger.warning('Shelf already exists in the database.')
                    return None  # Return None if shelf already exists

                # Generate a UUID for the shelf
                shelf_uuid = str(uuid.uuid4())
                # Get current date and time
                current_datetime = datetime.now()

                # Create a new Shelf instance
                new_shelf = Shelf(
                    uuid=shelf_uuid,
                    shelf_name=shelf_name,
                    kobo_should_sync=0,
                    date_added=current_datetime,
                    date_updated=current_datetime
                )

                # Add the new shelf to the session and commit
                session.add(new_shelf)
                session.commit()
                logger.info('Inserted shelf into the database.')

                # Return the UUID generated for the inserted shelf
                return shelf_uuid

        except IntegrityError:
            logger.warning('UUID already exists in the database.')
            session.rollback()
        except Exception as e:
            logger.error(f"Error inserting shelf: {e}")
            session.rollback()
        finally:
            session.close()

class RemoveBookFromShelf(SyncDBManager):
    def __init__(self):
        super().__init__()

    def remove_book_from_shelf(self, book_id, shelf_id):
        with self.Session() as session:
            update_sync_status_processor = UpdateBookSyncStatus()

            try:
                # Query the database to find the book entry on the specified shelf
                book_on_shelf = session.query(BookShelfLinks).filter_by(book_id=book_id, shelf_id=shelf_id).first()

                if book_on_shelf is None:
                    logger.warning("No book found on the specified shelf.")
                    return False

                # Delete the book entry from the database
                session.delete(book_on_shelf)
                session.commit()

                logger.info("Book removed from shelf successfully.")
                update_sync_status_result = update_sync_status_processor.update_book_sync_status(book_id)
                return True

            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error removing book from shelf: {e}")
                return False
 
class AddBookToShelf(SyncDBManager):
    def __init__(self):
        super().__init__()

    def add_book_to_shelf(self, book_id, shelf_id):
        with self.Session() as session:
            update_sync_status_processor = UpdateBookSyncStatus()        
            try:
                date_added = datetime.now()
                new_book_on_shelf = BookShelfLinks(book_id=book_id, shelf_id=shelf_id, date_added=date_added)
                session.add(new_book_on_shelf)
                session.commit()
                update_sync_status_result = update_sync_status_processor.update_book_sync_status(book_id)
                logger.info('Book added to the shelf successfully.')
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding book to the shelf: {e}")
                return False