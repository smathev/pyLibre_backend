from pydantic import BaseModel, Field
from typing import Optional


class BookSchema(BaseModel):
    isbn: Optional[str] = Field(None, description="ISBN of the book")
    title: Optional[str] = Field(None, description="Title of the book")
    author: Optional[str] = Field(None, description="Author of the book")
    publisher: Optional[str] = Field(None, description="Publisher of the book")
    publication_date: Optional[str] = Field(None, description="Publication date of the book")
    description: Optional[str] = Field(None, description="Synopsis of the book")
    year: Optional[str] = Field(None, description="Year of publication of the book")
    language: Optional[str] = Field(None, description="Language of the book")
    uuid: Optional[str] = Field(None, description="UUID of the book")
    relative_base_path: Optional[str] = Field(None, description="Base path to the book directory")
    full_base_path: Optional[str] = Field(None, description="Full OS-dependent path to the book directory")
    epub_filename: Optional[str] = Field(None, description="Filename of the epub file")
    cover_filename: Optional[str] = Field(None, description="Filename of the cover image file")