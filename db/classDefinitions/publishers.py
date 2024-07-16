from sqlalchemy import Column, Integer, String
from .date_columns import TimestampMixin
from .shared_base import Base

class Publisher(Base, TimestampMixin):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    
    book_publisher_links = None
