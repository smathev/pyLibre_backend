# book_genres_links.py

from sqlalchemy import Column, Integer, ForeignKey, Boolean
from .shared_base import Base
from .date_columns import TimestampMixin

class BookGenreLinks(Base, TimestampMixin):
    __tablename__ = 'book_genres_links'

    id = Column(Integer, primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    book_id = Column(Integer, ForeignKey('books.id'))

    # Define the relationships to Author and Ebook
    genres = None
    book = None