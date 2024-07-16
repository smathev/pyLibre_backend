# ebook.py
from sqlalchemy import Column, Integer, ForeignKey
from .shared_base import Base
from .date_columns import TimestampMixin 

# Define BookShelfLinks class with a relationship to Ebook and Shelf
class BookShelfLinks(Base, TimestampMixin):
    __tablename__ = 'book_shelf_links'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    shelf_id = Column(Integer, ForeignKey('shelves.id'))
    
    #Relationships start out with none - but defined in configure_relationships.py
    book = None
    shelf = None