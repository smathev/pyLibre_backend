from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
#from pydantic.generics import GenericModel
import datetime

T = TypeVar("T")

# class BaseResponse(GenericModel, Generic[T]):
#     status: str
#     message: Optional[str] = None
#     data: Optional[T] = None

class BaseResponse(BaseModel, Generic[T]):
     status: str
     message: Optional[str] = None
     data: Optional[T] = None

class AuthTokenData(BaseModel):
    auth_token: str

class AuthorData(BaseModel):
    author_name: str

class SyncTokenResponse(BaseModel):
    # Define the fields based on your existing data structure
    books_last_modified: datetime.datetime
    books_last_created: datetime.datetime
    reading_state_last_modified: datetime.datetime
    
