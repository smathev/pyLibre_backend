from db.db_manager.sync_db_manager import SyncDBManager
from db.classDefinitions.book import Book
from db.classDefinitions.book_series_links import BookSeriesLinks
from db.classDefinitions.file_location import FileLocation
from db.classDefinitions.book_series import BookSeries
from db.classDefinitions.kobo_sync import KoboSync
from db.db_fts_methods import FTSTableManager
from datetime import datetime
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

class UpdateBookMetadataByID(SyncDBManager):
    def __init__(self):
        super().__init__()

    def update_book_metadata_by_id(self, book_id, data):        
        try:
            with self.Session() as session:
                # Get current date and time
                current_datetime = datetime.now()
                # Add date_updated to data dictionary
                data['date_updated'] = current_datetime

                # Find the book by ID
                book = session.query(Book).filter_by(id=book_id).first()
                if book is None:
                    logger.error(f"No book found with id {book_id}")
                    return False

                # Update Book metadata
                ebook_data = data.get('metadata_changes', {})
                for key, value in ebook_data.items():
                    setattr(book, key, value)

                # Update BookSeriesLinks if available
                book_series_links_data = data.get('book_series_links', {})
                if book_series_links_data:
                    series_title = book_series_links_data.get('series_titles')
                    number_in_series = book_series_links_data.get('number_in_series')

                    # Check if the series exists in the BookSeries table
                    book_series = session.query(BookSeries).filter_by(series_title=series_title).first()
                    if book_series:
                        # Check if the book is already linked to the series in BookSeriesLinks
                        existing_link = session.query(BookSeriesLinks).filter_by(book_id=book_id, book_series_id=book_series.id).first()
                        if existing_link:
                            # Update number_in_series if it's different
                            if existing_link.number_in_series != number_in_series:
                                existing_link.number_in_series = number_in_series
                        else:
                            # Create a new link
                            new_link = BookSeriesLinks(book_id=book_id, 
                                                    book_series_id=book_series.id, 
                                                    number_in_series=number_in_series,
                                                    date_updated=current_datetime)
                            session.add(new_link)
                    else:
                        # Create a new BookSeries instance
                        book_series = BookSeries(series_title=series_title)
                        session.add(book_series)
                        session.commit()  # Commit to generate the primary key
                        # Create a new link
                        new_link = BookSeriesLinks(book_id=book_id, 
                                                book_series_id=book_series.id, 
                                                number_in_series=number_in_series,
                                                date_updated=current_datetime)
                        session.add(new_link)

                # Update FileLocation if available
                file_location_data = data.get('file_location', {})
                if file_location_data:
                    # Check if the book already has a file_location
                    if book.file_location:
                        file_location = book.file_location
                    else:
                        # If not, create a new FileLocation instance and associate it with the book
                        file_location = FileLocation()
                        book.file_location = file_location

                    # Update the attributes of the file_location
                    for key, value in file_location_data.items():
                        setattr(file_location, key, value)
                kobo_should_sync = data.get('kobo_should_sync')
                sync_record = session.query(KoboSync).filter(KoboSync.book_id == book_id).first()
                if sync_record:
                    sync_record.kobo_should_sync = 1 if kobo_should_sync == 1 else 0
                else:
                    new_sync_record = KoboSync(
                        book_id=book_id,
                        kobo_should_sync=1 if kobo_should_sync == 1 else 0,
                        date_added=current_datetime
                    )
                    session.add(new_sync_record)
                # Commit the changes
                session.commit()
                logger.info(f"Metadata updated for id {book_id}: {data}")
                update_fts_table_processor = FTSTableManager()
                update_fts_table_processor.update_fts_table(book)
                logger.info('Updated FTS table.')
                return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"SQLAlchemyError updating metadata for id {book_id}: {e}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating metadata for id {book_id}: {e}")
            return False
        finally:
            session.close()
