from db.db_manager.sync_db_manager import SyncDBManager
import json
from db.classDefinitions.book import Book
from db.classDefinitions.book_author_links import BookAuthorLinks
from db.classDefinitions.book_series_links import BookSeriesLinks
from db.classDefinitions.file_location import FileLocation
from db.classDefinitions.book_series import BookSeries
from db.classDefinitions.kobo_sync import KoboSync
from db.db_fts_methods import FTSTableManager
from datetime import datetime
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
        
class UpdateBook_SingleItem(SyncDBManager):
    def __init__(self):
        super().__init__()
    
    def update_single_metadata_item_book(self, book_id, column_to_update, new_value):
        try:
            with self.Session() as session:
                # Get current date and time
                current_datetime = datetime.now()
                # Create a dictionary with the column to update and the new value
                data = {column_to_update: new_value, 'date_updated': current_datetime}
                
                # Find the book by ID
                book = session.query(Book).filter_by(id=book_id).first()
                if book is None:
                    logger.error(f"No book found with id {book_id}")
                    return False
                
                # Update Book metadata
                for key, value in data.items():
                    setattr(book, key, value)
                
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"An error occurred: {e}")
            return False
        
class DeleteBook(SyncDBManager):
    def __init__(self):
        super().__init__()
    
    def delete_book(self, book_id):
        try:
            with self.Session() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                if book is None:
                    logger.error(f"No book found with id {book_id}")
                    return False
                
                # Delete the book
                session.delete(book)
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"An error occurred: {e}")
            return False