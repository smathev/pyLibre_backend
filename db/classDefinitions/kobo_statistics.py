from sqlalchemy import Column, Integer, ForeignKey
from .date_columns import TimestampMixin
from .shared_base import Base

class KoboStatistics(Base, TimestampMixin):
    __tablename__ = 'kobo_statistics'

    id = Column(Integer, primary_key=True)
    kobo_reading_state_id = Column(Integer, ForeignKey('kobo_reading_state.id'))
    remaining_time_minutes = Column(Integer)
    spent_reading_minutes = Column(Integer)