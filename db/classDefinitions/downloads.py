from sqlalchemy import Column, Integer, ForeignKey
from .date_columns import TimestampMixin 
from .shared_base import Base

class Downloads(Base, TimestampMixin):
    __tablename__ = 'downloads'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))

