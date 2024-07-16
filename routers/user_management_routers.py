from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.db_user_management import create_user, delete_user, authenticate_user
from schemas.user_management_schema import UserCreate, UserDelete, Token
from models.user_dependencies import get_current_user, TokenData, get_admin_user

from constants.application_constants import ACCESS_TOKEN_EXPIRE_MINUTES

from models.utils_jwt import create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/users/create_user", response_model=UserCreate, tags=["User Management"])
async def api_create_user(user: UserCreate, current_user: TokenData = Depends(get_admin_user)):
    try:
        db_user = await create_user(user)        
        if db_user is None:
            raise HTTPException(status_code=400, detail="User creation failed.")
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User creation failed: {e}")

@router.delete("/users/delete_user/{user_id}", response_model=UserDelete, tags=["User Management"])
async def api_delete_user(user: UserDelete, current_user: TokenData = Depends(get_admin_user)):
    try:
        user = await delete_user(user.id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"id": user.id, "name": user.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User deletion failed: {e}")

@router.post("/users/get_token", response_model=Token, tags=["User Management"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", tags=["User Management"])
async def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return current_user