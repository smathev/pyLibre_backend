# async_db_manager.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from .base_db_manager import BaseDBManager
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine

class AsyncDBManager(BaseDBManager):
    def __init__(self):
        super().__init__()
        self.async_engine = create_async_engine(f'sqlite+aiosqlite:///{self.db_file}', echo=True)
        self.AsyncSession = sessionmaker(bind=self.async_engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def get_session(self):
        async with self.AsyncSession() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

