# author.py

from sqlalchemy import Column, Integer, String
from .date_columns import TimestampMixin
from .shared_base import Base

# Define Author class
class Author(Base, TimestampMixin):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    birthday = Column(String)

    # Define the relationship to BookAuthorLinks
    book_author_links = None
