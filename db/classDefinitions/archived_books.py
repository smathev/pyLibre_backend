from sqlalchemy import Column, Integer, ForeignKey, Boolean
from .date_columns import TimestampMixin
from .shared_base import Base


# Baseclass representing books that are archived on the user's Kobo device.
class ArchivedBook(Base, TimestampMixin):
    __tablename__ = 'archived_book'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    book_id = Column(Integer)
    is_archived = Column(Boolean, unique=False)