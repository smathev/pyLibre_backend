from fastapi import APIRouter, HTTPException
from loguru import logger
from db.edit_authors import EditAuthors 
from sqlalchemy.exc import SQLAlchemyError
from schemas.response_model import ResponseModel

router = APIRouter()

edit_authors_processor = EditAuthors()

@router.post('/edit_author/create_new_author', response_model=ResponseModel, status_code=200, description="Create a new author", summary="Create a new author", tags=["Edit Author"])
async def create_new_author(author_name: str):
    try:
        result = await edit_authors_processor.add_author(author_name)
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"Error creating new author: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/edit_author/delete_author/{author_id}', response_model=ResponseModel, status_code=200, description="Delete an author", summary="Delete an author", tags=["Edit Author"])
async def delete_author(author_id: int):
    try:
        result = await edit_authors_processor.delete_author(author_id)
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"Error deleting author: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/edit_author/change_author_birth_date/{author_id}/{birth_date}', response_model=str, status_code=200, description="Change the birth date of an author", summary="Change the birth date of an author", tags=["Edit Author"])
async def change_author_birth_date(author_id: int, birth_date: str):
    pass

@router.post('/edit_author/change_author_name/{author_id}', response_model=ResponseModel, status_code=200, description="Change the authors name", summary="Change the name of an author", tags=["Edit Author"])
async def change_author_birth_date(author_id: int, author_name: str):
    try:
        result = await edit_authors_processor.change_author_name(author_id, author_name)
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"Error updating author name: {e}")
        raise HTTPException(status_code=500, detail=str(e))