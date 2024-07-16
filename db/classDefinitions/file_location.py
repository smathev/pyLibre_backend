# class_definitions/file_location.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from .date_columns import TimestampMixin 
from .shared_base import Base

# Define FileLocation class with a relationship to Ebook
class FileLocation(Base, TimestampMixin):
    __tablename__ = 'file_location'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), unique=True)
    relative_base_path = Column(String)
    full_base_path = Column(String)
    epub_filename = Column(String)
    kepub_filename = Column(String)
    cover_filename = Column(String)

    # Establish relationship with Ebook
    book = None
