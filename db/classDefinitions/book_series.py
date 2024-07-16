# book_series.py

from sqlalchemy import Column, Integer, String
from .date_columns import TimestampMixin 
from .shared_base import Base

# Define FileLocation class with a relationship to Ebook
class BookSeries(Base, TimestampMixin):
    __tablename__ = 'book_series'

    id = Column(Integer, primary_key=True)
    series_title = Column(String)

    # Define the relationship to BookInSeries
    book_series_links = None