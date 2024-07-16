from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar
#from pydantic.generics import GenericModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Generic response model
T = TypeVar("T")

# class BaseResponse(GenericModel, Generic[T]):
#     status: str = Field(..., example="success")
#     message: Optional[str] = Field(None, example="Operation completed successfully")
#     data: Optional[T] = None
#
class BaseResponse(BaseModel, Generic[T]):
    status: str = Field(..., example="success")
    message: Optional[str] = Field(None, example="Operation completed successfully")
    data: Optional[T] = None

# Specific response models
class BookDetails(BaseModel):
    title: Optional[str] = None 
    isbn: Optional[str] = None 
    genre: Optional[str] = None 
    description: Optional[str] = None 
    series_titles: Optional[str] = None 
    number_in_series: Optional[str] = None 

class AddDeleteAuthorSchema(BaseModel):
    author_id: int 
    book_id: int
    primary_author: Optional[bool] = False

class UpdateBookTitle(BaseModel):
    book_id: int
    new_title: str

class UpdateBookMetadata(BaseModel):
    book_id: int
    new_string: str

class BookDetailsResponse(BaseResponse[BookDetails]):
    pass

class AddDeleteAuthorResponse(BaseResponse[AddDeleteAuthorSchema]):
    pass

class UpdateBookTitleResponse(BaseResponse[UpdateBookTitle]):
    pass

class UpdateBookMetadataResponse(BaseResponse[UpdateBookMetadata]):
    pass
