from sqlalchemy import Column, Integer, ForeignKey
from .date_columns import TimestampMixin
from .shared_base import Base

class BookPublisherLinks(Base, TimestampMixin):
    __tablename__ = 'book_publishers_links'

    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    publisher_id = Column(Integer, ForeignKey('publishers.id'), primary_key=True)
    # Relationships
    book = None 
    publisher = None