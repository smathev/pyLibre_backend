# ebook.py

from sqlalchemy import Column, Integer, String
from .date_columns import TimestampMixin
from .shared_base import Base

# Define book class
class Book(Base, TimestampMixin):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    isbn = Column(String, unique=True)
    title = Column(String)
    publication_date = Column(String)
    year = Column(String)
    language = Column(String)
    genre = Column(String)
    description = Column(String)
    uuid = Column(String, unique=True)

    # Define relationships
    book_author_links = None
    file_location = None
    kobo_syncs = None
    book_shelf_links = None
    book_series_links = None
    book_publisher_links = None