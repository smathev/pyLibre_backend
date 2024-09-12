from db.classDefinitions.book import Book
from db.classDefinitions.file_location import FileLocation
from db.classDefinitions.kobo_sync import KoboSync
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.book_shelf_links import BookShelfLinks
from db.classDefinitions.book_series import BookSeries
from db.classDefinitions.book_series_links import BookSeriesLinks
from db.classDefinitions.publishers import Publisher
from db.classDefinitions.book_publisher_links import BookPublisherLinks
from db.classDefinitions.kobo_reading_state import KoboReadingState
from db.classDefinitions.read_book import ReadBook
from db.classDefinitions.kobo_bookmark import KoboBookmark
from db.classDefinitions.kobo_statistics import KoboStatistics

from db.classDefinitions.downloads import Downloads


from db.classDefinitions.user import User
from db.classDefinitions.remote_auth_token import RemoteAuthToken

from db.classDefinitions.author import Author
from db.classDefinitions.book_author_links import BookAuthorLinks

from db.classDefinitions.genres import Genres
from db.classDefinitions.book_genre_links import BookGenreLinks

from sqlalchemy.orm import relationship, backref
from loguru import logger

class ConfigureRelationships:
    def __init__(self):
        super().__init__()

    def configure_relationships(self, session):
        try:

            Book.book_publisher_links = relationship('BookPublisherLinks', back_populates='book', cascade="all, delete, save-update")
            Publisher.book_publisher_links = relationship('BookPublisherLinks', back_populates='publisher', cascade="all, delete, save-update")
            BookPublisherLinks.book = relationship('Book', back_populates='book_publisher_links')
            BookPublisherLinks.publisher = relationship('Publisher', back_populates='book_publisher_links')

            ReadBook.kobo_reading_state = relationship("KoboReadingState", uselist=False,
                                      primaryjoin="and_(ReadBook.user_id == foreign(KoboReadingState.user_id), "
                                                  "ReadBook.book_id == foreign(KoboReadingState.book_id))",
                                      cascade="all",
                                      backref=backref("book_read_link",
                                                      uselist=False))

            Book.book_author_links = relationship("BookAuthorLinks", back_populates="book", cascade="all, delete, save-update")
            Author.book_author_links = relationship("BookAuthorLinks", back_populates="author", cascade="all, delete, save-update")
            BookAuthorLinks.book = relationship("Book", back_populates="book_author_links", cascade="save-update")
            BookAuthorLinks.author = relationship("Author", back_populates="book_author_links", cascade="save-update")
            
            Book.book_genre_links = relationship("BookGenreLinks", back_populates="book", cascade="all, delete, save-update")
            Genres.book_genre_links = relationship("BookGenreLinks", back_populates="genre", cascade="all, delete, save-update")            
            BookGenreLinks.book = relationship("Book", back_populates="book_genre_links", cascade="save-update")
            BookGenreLinks.genre = relationship("Genres", back_populates="book_genre_links", cascade="save-update")

            User.remote_auth_token = relationship('RemoteAuthToken', back_populates='user', cascade="all, delete, save-update")
            User.shelf = relationship('Shelf', back_populates='user', order_by='Shelf.shelf_name')

            RemoteAuthToken.user = relationship('User', back_populates='remote_auth_token', single_parent=True, cascade="all, delete, save-update")
            Shelf.user = relationship('User', back_populates='shelf')
            
            KoboReadingState.current_bookmark = relationship("KoboBookmark", uselist=False, backref="kobo_reading_state", cascade="all, delete")
            KoboReadingState.statistics = relationship("KoboStatistics", uselist=False, backref="kobo_reading_state", cascade="all, delete")

            Book.file_location = relationship("FileLocation", uselist=False, back_populates="book", cascade="all, delete, save-update")
            FileLocation.book = relationship("Book", back_populates="file_location", cascade="all, delete-orphan, save-update", single_parent=True)

            Book.kobo_sync = relationship("KoboSync", uselist=False, back_populates="book", cascade="all, delete, save-update")            
            KoboSync.book = relationship("Book", back_populates="kobo_sync", cascade="all, delete-orphan, save-update", single_parent=True)
            
            Book.book_shelf_links = relationship("BookShelfLinks", back_populates="book")
            Shelf.book_shelf_links = relationship("BookShelfLinks", back_populates="shelf")
            BookShelfLinks.book = relationship("Book", back_populates="book_shelf_links")
            BookShelfLinks.shelf = relationship("Shelf", back_populates="book_shelf_links")

            Book.book_series_links = relationship("BookSeriesLinks", back_populates="book", cascade="all, delete, save-update")
            BookSeries.book_series_links = relationship("BookSeriesLinks", back_populates="book_series", cascade="all, delete, save-update")
            BookSeriesLinks.book = relationship("Book", back_populates="book_series_links", cascade="all, delete, save-update")
            BookSeriesLinks.book_series = relationship("BookSeries", back_populates="book_series_links", cascade="all, delete, save-update")
            
            User.downloads = relationship('Downloads', backref='user', lazy='dynamic')

            # Commit the session to save changes to the database
            session.commit()
            logger.info('Relationships configured successfully.')
        except Exception as e:
            session.rollback()  # Rollback the session in case of error
            logger.error(f"Error configuring relationships: {e}")
        finally:
            session.close()  # Close the session to free resources
