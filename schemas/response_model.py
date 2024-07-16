from pydantic import BaseModel
from typing import Optional

class ResponseModel(BaseModel):
    status: Optional[str] = None 
    message: Optional[str] = None