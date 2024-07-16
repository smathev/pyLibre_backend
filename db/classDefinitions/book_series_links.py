# book_series_links.py

from sqlalchemy import Column, Integer, ForeignKey
from .shared_base import Base
from .date_columns import TimestampMixin 

class BookSeriesLinks(Base, TimestampMixin):
    __tablename__ = 'book_series_links'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    book_series_id = Column(Integer, ForeignKey('book_series.id'))
    number_in_series = Column(Integer)

    book_series = None
    book = None