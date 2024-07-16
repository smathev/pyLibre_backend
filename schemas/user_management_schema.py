from pydantic import BaseModel
from typing import Optional, Dict
import constants.user_constants as constants

class UserCreate(BaseModel):
    name: str
    email: str = ""
    role: int = 0
    password: str = f"{constants.DEFAULT_PASSWORD}"
    kindle_mail: Optional[str] = ""
    locale: Optional[str] = "en"
    sidebar_view: int = 1
    default_language: str = "all"
    denied_tags: Optional[str] = ""
    allowed_tags: Optional[str] = ""
    denied_column_value: Optional[str] = ""
    allowed_column_value: Optional[str] = ""
    view_settings: Optional[Dict] = {}
    kobo_only_shelves_sync: int = 0

class UserDelete(BaseModel):
    id: int
    name: Optional[str] = ""

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str = None
    role: int