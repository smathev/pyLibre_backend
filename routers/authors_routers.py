from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from db.fetch_data_operations import FetchAuthorsAndNumberOfBooks
from db.edit_authors import EditAuthors

from schemas.response_models import BaseResponse, AuthorData

router = APIRouter()

@router.get('/authors/serve_authors', tags=["authors"], response_model=BaseResponse)
def serve_shelves():
    try:
        fetch_authors_processor = FetchAuthorsAndNumberOfBooks() 
        results = fetch_authors_processor.fetch_authors_and_number_of_books()
        return BaseResponse(status='success', message='Authors fetched successfully', data=results)  

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/authors/create_new_author', tags=["authors"], response_model=BaseResponse)
async def create_new_author(request: Request):
    try:
        data = await request.json()
        author_name = data['author_name']
        author_creator = EditAuthors() 
        new_author = await author_creator.add_author(author_name)
        return new_author

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))
