from pydantic import BaseModel
from typing import Optional

class MobiISBN(BaseModel):
    isbn: Optional[str] = None


