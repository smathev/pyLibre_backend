from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from .date_columns import TimestampMixin
from .shared_base import Base

class Bookmark(Base, TimestampMixin):
    __tablename__ = 'bookmark'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    book_id = Column(Integer)
    format = Column(String(collation='NOCASE'))
    bookmark_key = Column(String)