from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar

logger = logging.getLogger(__name__)

router = APIRouter()

# Generic response model
T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    status: str = Field(..., example="success")
    message: Optional[str] = Field(None, example="Operation completed successfully")
    data: Optional[T] = None

# Specific response models
class GenreDetails(BaseModel):
    genre_id: Optional[int] = None
    genre_name: Optional[str] = None
    description: Optional[str] = None

class AddDeleteGenreSchema(BaseModel):
    genre_id: int
    book_id: int

class UpdateGenreName(BaseModel):
    genre_id: int
    new_genre_name: str

class GenreDetailsResponse(BaseResponse[GenreDetails]):
    pass

class AddDeleteGenreResponse(BaseResponse[AddDeleteGenreSchema]):
    pass

class UpdateGenreNameResponse(BaseResponse[UpdateGenreName]):
    pass
