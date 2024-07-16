# shelf.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .date_columns import TimestampMixin 
from .shared_base import Base

# Define Shelf class with a relationship to BookShelfLinks
class Shelf(Base, TimestampMixin):
    __tablename__ = 'shelves'

    id = Column(Integer, primary_key=True)
    shelf_name = Column(String, unique=True)
    uuid = Column(String)
    is_public = Column(Integer, default=0)
    kobo_should_sync = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('user.id')) 
    book_shelf_links = None
    user = None