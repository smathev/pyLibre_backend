from sqlalchemy.future import select
import sqlite3
from db.db_manager.async_db_manager import AsyncDBManager 
from db.db_manager.sync_db_manager import SyncDBManager
from db.classDefinitions.file_location import FileLocation
from db.classDefinitions.book import Book
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.book_shelf_links import BookShelfLinks

from db.classDefinitions.author import Author
from db.classDefinitions.book_author_links import BookAuthorLinks
from db.classDefinitions.publishers import Publisher
from db.classDefinitions.book_publisher_links import BookPublisherLinks
from sqlalchemy.orm import joinedload, subqueryload, selectinload
import os
from loguru import logger
import asyncio

class FetchCoverImageFromDB(AsyncDBManager):
    def __init__(self):
        super().__init__()

    async def fetch_cover_image_by_id(self, id):
        async with self.get_session() as session:
            try:
                # Use select() to construct the SQL expression
                stmt = select(FileLocation).where(FileLocation.id == id)
                result = await session.execute(stmt)
                file_location = result.scalars().first()

                if file_location:
                    # Construct and return a dictionary with cover image data
                    cover_image_data = {
                        'relative_base_path': file_location.relative_base_path,
                        'cover_filename': file_location.cover_filename
                    }
                    logger.info('Fetched cover image from the database by UUID.')
                    return cover_image_data
                else:
                    logger.warning('Cover image not found in the database by UUID.')
                    return None
            except Exception as e:
                logger.error(f"Error fetching cover image: {e}")
                return None

class FetchBooksFromDB(AsyncDBManager):
    def __init__(self):
        super().__init__()

    async def fetch_books_from_database(self):
        async with self.get_session() as session:
            try:
                # Modify the loading strategy if necessary or simplify if you're encountering issues
                stmt = select(Book).options(
                    selectinload(Book.book_author_links).selectinload(BookAuthorLinks.author),
                    selectinload(Book.file_location),
                    selectinload(Book.book_publisher_links).selectinload(BookPublisherLinks.publisher),
                )
                result = await session.execute(stmt)
                books_data = result.scalars().all()  # No 'await' here as it's not awaitable

                books_list = [
                    {
                        'id': book.id,
                        'isbn': book.isbn,
                        'title': book.title,
                        'authors': [book_author_links.author.name for book_author_links in book.book_author_links],
                        'publishers': [book_publisher_links.publisher.name for book_publisher_links in book.book_publisher_links],
                        'year': book.year,
                        'language': book.language,
                        'uuid': book.uuid,
                        'cover_image_path': os.path.join(book.file_location.full_base_path, book.file_location.cover_filename),
                        'epub_filename': book.file_location.epub_filename,
                        'kepub_filename': book.file_location.kepub_filename
                    } for book in books_data
                ]
                logger.info('Fetched all books from the database.')
                return books_list

            except Exception as e:
                logger.error(f"Error fetching books from database: {e}")
                raise  # Properly propagate exceptions up to the caller

class FetchBookDetailsFromDB(SyncDBManager):
    def __init__(self):
        super().__init__()
    def fetch_book_details_by_id(self, id: int):
        return self._fetch_book_details(id=id)

    def fetch_book_details_by_uuid(self, uuid: str):
        return self._fetch_book_details(uuid=uuid)

    def _fetch_book_details(self, id=None, uuid=None):
        try:
            with self.Session() as session:
                if id is not None:
                    book = session.query(Book).filter_by(id=id).first()
                elif uuid is not None:
                    book = session.query(Book).filter_by(uuid=uuid).first()
                else:
                    logger.error("Either id or uuid must be provided.")
                    return None

                if book:
                    # Access the associated FileLocation directly from the Book object
                    file_location = book.file_location

                    # Gather series information including series titles and number in series
                    series_info = [
                        {
                            'series_title': bis.book_series.series_title,
                            'number_in_series': bis.number_in_series
                        }
                        for bis in book.book_series_links
                    ]
                    authors_info = [ 
                        {
                            'author_name': book_author_link.author.name, 
                            'author_id': book_author_link.author_id,
                            'primary_author': book_author_link.primary_author
                        }
                            for book_author_link in book.book_author_links]
                    publisher_info = [ 
                        {
                            'publisher_name': book_publisher_link.publisher.name, 
                            'publisher_id': book_publisher_link.publisher_id
                        }
                            for book_publisher_link in book.book_publisher_links]
                    # Create book_details dictionary
                    book_details = {
                        'id': book.id,
                        'isbn': book.isbn,
                        'genre': book.genre,
                        'title': book.title,
                        'description': book.description,
                        'authors': authors_info,
                        'publishers': publisher_info,
                        'year': book.year,
                        'language': book.language,
                        'uuid': book.uuid,
                        'relative_base_path': file_location.relative_base_path,
                        'full_base_path': file_location.full_base_path,
                        'epub_filename': file_location.epub_filename,
                        'cover_filename': file_location.cover_filename,
                        'series_info': series_info  # Store series info including titles and numbers
                    }
                    logger.info('Fetched book details from the database.')
                    return book_details
                else:
                    logger.warning('Book not found in the database.')
                    return None
        except Exception as e:
            logger.error(f"Error fetching book details: {e}")
            return None
        

class FetchShelvesAndBooksOnShelves(SyncDBManager):
    def fetch_shelves_and_books(self):
        try:
            with self.Session() as session:
                # Fetch shelves with related books using eager loading
                shelves = session.query(Shelf).options(
                    joinedload(Shelf.book_shelf_links).joinedload(BookShelfLinks.book)
                ).all()

                shelves_data = []
                for shelf in shelves:
                    shelf_data = {
                        "id": shelf.id,
                        "shelf_name": shelf.shelf_name,
                        "uuid": shelf.uuid,
                        "kobo_should_sync": shelf.kobo_should_sync,
                        "date_added": shelf.date_added,
                        "date_updated": shelf.date_updated,
                        "books": []  # Placeholder for books
                    }

                    for book_on_shelf in shelf.book_shelf_links:
                        book = book_on_shelf.book
                        if book:
                            shelf_data["books"].append({
                                "id": book.id,
                                "title": book.title
                            })

                    # Count the number of books for the shelf
                    shelf_data["num_books"] = len(shelf_data["books"])
                    shelves_data.append(shelf_data)

                return shelves_data

        except Exception as e:
            logger.error(f"Error fetching shelves and books: {e}")
            return None

class FetchShelvesFromDB(SyncDBManager):
    def fetch_shelves(self):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            # Fetch shelves
            c.execute("SELECT * FROM shelves")
            shelves = []
            for row in c.fetchall():
                shelf = {
                    "id": row[0],
                    "shelf_name": row[1],
                    "uuid": row[2],
                    "kobo_should_sync": row[3],
                    "date_added": row[4],
                    "date_updated": row[5],
                    "books": []  # Placeholder for books
                }
                shelves.append(shelf)

            return shelves

        except sqlite3.Error as e:
            logger.error(f"Error fetching shelves and books: {e}")

class FetchAuthorsAndNumberOfBooks(SyncDBManager):
    def fetch_authors_and_number_of_books(self):
        try:
            with self.Session() as session:
                # Fetch shelves with related books using eager loading
                authors = session.query(Author).options(
                    joinedload(Author.book_author_links).joinedload(BookAuthorLinks.book)
                ).all()

                authors_data = []
                for author in authors:
                    author_data = {
                        "id": author.id,
                        "name": author.name,
                        "birthday": author.birthday,
                        "date_added": author.date_added,
                        "date_updated": author.date_updated,
                        "books": []  # Placeholder for books
                    }

                    for book_author_links in author.book_author_links:
                        book = book_author_links.book
                        if book:
                            author_data["books"].append({
                                "id": book.id,
                                "title": book.title
                            })

                    # Count the number of books for the shelf
                    author_data["num_books"] = len(author_data["books"])
                    authors_data.append(author_data)

                return authors_data

        except sqlite3.Error as e:
            logger.error(f"Error fetching authors and books: {e}")
