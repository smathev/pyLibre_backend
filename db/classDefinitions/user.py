#user.py
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, JSON

from .date_columns import TimestampMixin 
from .shared_base import Base
from db.class_methods.user_methods import UserBase


class User(Base, TimestampMixin, UserBase):
    __tablename__ = 'user'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    email = Column(String(120), unique=True, default="")
    role = Column(SmallInteger, default='USER')
    password = Column(String)
    kindle_mail = Column(String(120), default="")
    locale = Column(String(2), default="en")
    sidebar_view = Column(Integer, default=1)
    default_language = Column(String(3), default="all")
    denied_tags = Column(String, default="")
    allowed_tags = Column(String, default="")
    denied_column_value = Column(String, default="")
    allowed_column_value = Column(String, default="")
    view_settings = Column(JSON, default={})
    kobo_only_shelves_sync = Column(Integer, default=0)

    shelf = None
    remote_auth_token = None
    downloads = None