from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from loguru import logger
from .classDefinitions.user import User

from .db_manager.async_db_manager import AsyncDBManager
from schemas.user_management_schema import UserCreate, UserDelete
from models.utils_jwt import get_password_hash, verify_password
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: UserCreate):
    async_db_manager = AsyncDBManager()
    async with async_db_manager.get_session() as session:
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                name=user.name,
                email=user.email,
                role=user.role,
                password=hashed_password,
                kindle_mail=user.kindle_mail,
                locale=user.locale,
                sidebar_view=user.sidebar_view,
                default_language=user.default_language,
                denied_tags=user.denied_tags,
                allowed_tags=user.allowed_tags,
                denied_column_value=user.denied_column_value,
                allowed_column_value=user.allowed_column_value,
                view_settings=user.view_settings,
                kobo_only_shelves_sync=user.kobo_only_shelves_sync,
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error creating user: {e}")
            raise

async def authenticate_user(username: str, password: str):
    async_db_manager = AsyncDBManager()
    async with async_db_manager.get_session() as session:
        stmt = select(User).filter(User.name == username)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user and verify_password(password, user.password):
            return user
        return None

async def delete_user(user_id: int):
    async_db_manager = AsyncDBManager()
    async with async_db_manager.get_session() as session:
        try:
            user = await session.get(User, user_id)
            if user is None:
                logger.error(f"User with ID {user_id} not found.")
                return None
            await session.delete(user)
            await session.commit()
            logger.info(f"User with ID {user_id} deleted successfully.")
            return user
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error deleting user: {e}")
            raise


