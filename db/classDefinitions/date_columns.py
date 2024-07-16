from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class TimestampMixin:
    @declared_attr
    def date_added(cls):
        return Column(DateTime, default=datetime.now)

    @declared_attr
    def date_updated(cls):
        return Column(DateTime, default=datetime.now, onupdate=datetime.now)
