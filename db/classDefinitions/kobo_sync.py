# ebook.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from .date_columns import TimestampMixin 
from .shared_base import Base

# Define KoboSync class with a relationship to Ebook
class KoboSync(Base, TimestampMixin):
    __tablename__ = 'kobo_syncs'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    kobo_synced = Column(Boolean, default=False)
    kobo_should_sync = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    book = None