from db.db_manager.sync_db_manager import SyncDBManager
from db.classDefinitions.book import Book
from db.classDefinitions.file_location import FileLocation

from db.classDefinitions.author import Author
from db.classDefinitions.book_author_links import BookAuthorLinks

from db.classDefinitions.publishers import Publisher
from db.classDefinitions.book_publisher_links import BookPublisherLinks

from db.classDefinitions.kobo_sync import KoboSync

from db.db_fts_methods import FTSTableManager
from datetime import datetime
from loguru import logger
import uuid

class InsertNewBookMetadata(SyncDBManager):
    def __init__(self):
        super().__init__()

    def insert_new_book_metadata(self, metadata):  
        try:
            with self.Session() as session:
                # Check if the combination of author and title already exists
                existing_book = session.query(Book).filter_by(title=metadata.get('title')).first()
                if existing_book:
                    logger.warning('Metadata already exists in the database.')
                    return None  # Return None if metadata already exists

                # Check if the ISBN already exists
                if metadata.get('isbn'):
                    existing_isbn = session.query(Book).filter_by(isbn=metadata.get('isbn')).first()
                    if existing_isbn:
                        logger.warning('ISBN already exists in the database.')
                        return None

                # Generate a UUID for the new book
                metadata_uuid = str(uuid.uuid4())
                current_datetime = datetime.now()  # Current timestamp for the new entries

                # Check if the author exists in the database, if not, create a new author
                author_name = metadata.get('author')
                author = session.query(Author).filter_by(name=author_name).first()
                if not author:
                    # Create a new Author object
                    author = Author(name=author_name,
                                    date_added=current_datetime
                                    )
                    session.add(author)
                    session.commit()

                publisher_name = metadata.get('publisher')
                if publisher_name is not None:
                    publisher = session.query(Publisher).filter_by(name=publisher_name).first()
                else:
                    publisher = None
                if publisher_name is not None:
                    # Create a new Publisher object
                    publisher = Publisher(name=publisher_name,
                                    date_added=current_datetime
                                    )
                    session.add(publisher)
                    session.commit()


                # Create a new Ebook object
                new_book = Book(
                    isbn=metadata.get('isbn'),
                    title=metadata.get('title'),
                    publication_date=metadata.get('publication_date'),
                    year=metadata.get('year'),
                    language=metadata.get('language'),
                    description=metadata.get('description'),
                    uuid=metadata_uuid,
                    date_added=current_datetime
                )

                # Check if there is already a primary author for the book
                primary_author_exists = session.query(BookAuthorLinks).filter_by(book_id=new_book.id, primary_author=1).first()

                # If no primary author exists, make the current author the primary author
                primary_author_flag = 1 if not primary_author_exists else 0

                # Associate the Author with the book through BookAuthorLinks
                author_of_book = BookAuthorLinks(author=author, book=new_book, primary_author=primary_author_flag)
                session.add(author_of_book)

                if publisher is not None:
                    # Associate the pubisher with the book through BookPublishersLinks
                    publisher_of_book = BookPublisherLinks(publisher=publisher, book=new_book)
                    session.add(publisher_of_book)


                # Create a new FileLocation object
                file_location = FileLocation(
                    relative_base_path=metadata.get('relative_base_path'),
                    full_base_path=metadata.get('full_base_path'),
                    epub_filename=metadata.get('epub_filename'),
                    cover_filename=metadata.get('cover_filename'),
                    date_added=current_datetime
                )

                # Associate the FileLocation with the Ebook
                new_book.file_location = file_location

                # Create a new FileLocation object
                kobo_sync = KoboSync(
                    kobo_synced=False,
                    kobo_should_sync=False,
                    date_added=current_datetime
                )
                new_book.kobo_sync = kobo_sync
                # Add the new Ebook to the session and commit
                session.add(new_book)
                session.commit()
                

                logger.info('Inserted metadata into the database.')
                try:
                    update_fts_table_processor = FTSTableManager()
                    update_fts_table_processor.update_fts_table(new_book)
                    logger.info('Updated FTS table.')
                except Exception as e:
                    logger.error(f"Failed to update FTS table for book id {book.id}: {e}")
                return metadata_uuid  # Return the UUID of the new entry
        except Exception as e:
            session.rollback()  # Roll back the transaction in case of error
            logger.error(f"Error inserting metadata: {e}")
            return None
        finally:
            session.close()  # Ensure the session is closed properly
