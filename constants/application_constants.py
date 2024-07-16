import secrets
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_secret_key():
    DEV_SECRET_KEY = secrets.token_urlsafe(32)
    return DEV_SECRET_KEY

ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.getenv("SECRET_KEY")