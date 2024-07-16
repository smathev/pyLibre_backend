from pydantic import BaseModel
from typing import List

class ShelfRequest(BaseModel):
    Name: str
    Items: List[str]