from sqlalchemy.future import select
from db.db_manager.async_db_manager import AsyncDBManager
from db.classDefinitions.author import Author
from loguru import logger
from schemas.response_models import (BaseResponse, 
                                     AuthorData)

class EditAuthors(AsyncDBManager):
    def __init__(self):
        super().__init__()

    async def delete_author(self, author_id):
        async with self.get_session() as session:
            try:
                author = await session.get(Author, author_id)
                if not author:
                    return BaseResponse(status='error', message='No such author found', data=None)
                
                await session.delete(author)
                await session.commit()
                return BaseResponse(status='success', message='Author removed', data=None)
            except Exception as e:
                logger.error(f"Error removing author: {e}")
                return BaseResponse(status='error', message=str(e), data=None)

    async def add_author(self, author_name):
        async with self.get_session() as session:
            try:
                result = await session.execute(select(Author).where(Author.name == author_name))
                author = result.scalars().first()
                if not author:
                    author = Author(name=author_name)
                    session.add(author)
                    await session.commit()
                    return BaseResponse(status='success', message='Author added', data=AuthorData(author_name=author_name))
                else:
                    return BaseResponse(status='error', message='Author already exists', data=None)
            except Exception as e:
                logger.error(f"Error adding author: {e}")
                return BaseResponse(status='error', message=str(e), data=None)
            
    async def change_author_name(self, author_id: int, new_author_name: str):
        async with self.get_session() as session:
            try:
                author = await session.get(Author, author_id)
                if not author:
                    return BaseResponse(status='error', message='No such author found', data=None)

                author.name = new_author_name
                session.add(author)
                await session.commit()
                return BaseResponse(status='success', message='Author name updated successfully', data=AuthorData(author_name=new_author_name))
            except Exception as e:
                logger.error(f"Error updating author name: {e}")
                return BaseResponse(status='error', message=str(e), data=None)