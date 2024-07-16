from sqlalchemy import Column, Integer, ForeignKey, String
from .shared_base import Base
from .date_columns import TimestampMixin

# This table keeps track of deleted Shelves so that deletes can be propagated to any paired Kobo device.
class ShelfArchive(Base, TimestampMixin):
    __tablename__ = 'shelf_archive'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))