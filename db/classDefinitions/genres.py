# genres.py

from sqlalchemy import Column, Integer, String
from .date_columns import TimestampMixin
from .shared_base import Base

# Define Genres class
class Genres(Base, TimestampMixin):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    genre_name = Column(String)

    # Define the relationship to BookGenreLinks
    book_genre_links = None
