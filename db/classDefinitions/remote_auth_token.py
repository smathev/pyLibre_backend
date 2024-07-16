from .date_columns import TimestampMixin 
from .shared_base import Base
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, JSON, ForeignKey, DateTime
import datetime
from binascii import hexlify
import os

class RemoteAuthToken(Base, TimestampMixin):
    __tablename__ = 'remote_auth_token'

    id = Column(Integer, primary_key=True)
    auth_token = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    verified = Column(Boolean, default=False)
    expiration = Column(DateTime)
    token_type = Column(Integer, default=0)
    user = None

    def __init__(self):
        self.auth_token = (hexlify(os.urandom(4))).decode('utf-8')
        self.expiration = datetime.datetime.now() + datetime.timedelta(minutes=10)  # 10 min from now

    def __repr__(self):
        return '<Token %r>' % self.id
