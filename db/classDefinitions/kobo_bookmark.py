from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from .date_columns import TimestampMixin
from .shared_base import Base

class KoboBookmark(Base, TimestampMixin):
    __tablename__ = 'kobo_bookmark'

    id = Column(Integer, primary_key=True)
    kobo_reading_state_id = Column(Integer, ForeignKey('kobo_reading_state.id'))
    location_source = Column(String)
    location_type = Column(String)
    location_value = Column(String)
    progress_percent = Column(Float)
    content_source_progress_percent = Column(Float)