from pydantic import BaseModel
from typing import Optional, List

class SearchQuery(BaseModel):
    search_query: Optional[str] = None
    id: Optional[int] = None

class Book(BaseModel):
    id: Optional[int] = None 
    title: Optional[str] = None 
    authors: Optional[str] = None 

class ResponseModel(BaseModel):
    results: List[Book]

class Author(BaseModel):
    id: Optional[int] = None 
    author: Optional[str] = None 