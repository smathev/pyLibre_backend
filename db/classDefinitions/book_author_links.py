# book_authors_links.py

from sqlalchemy import Column, Integer, ForeignKey, Boolean
from .shared_base import Base
from .date_columns import TimestampMixin

class BookAuthorLinks(Base, TimestampMixin):
    __tablename__ = 'book_authors_links'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    primary_author = Column(Boolean, default=False)
    book_id = Column(Integer, ForeignKey('books.id'))

    # Define the relationships to Author and Ebook
    author = None
    book = None