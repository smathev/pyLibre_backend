from fastapi import APIRouter, HTTPException

from loguru import logger
from models.utils_path_manager import path_manager
from fastapi.responses import FileResponse

from db.fetch_data_operations import FetchCoverImageFromDB, FetchBooksFromDB, FetchBookDetailsFromDB

router = APIRouter()

@router.get('/book_cover/{id}', tags=["books", "covers"])
async def serve_book_cover(id: str):
    cover_fetcher = FetchCoverImageFromDB()
    
    try:
        # Fetch the cover image data asynchronously
        cover_image_data = await cover_fetcher.fetch_cover_image_by_id(id)
        
        if cover_image_data and 'cover_filename' in cover_image_data and cover_image_data['cover_filename']:
            # Construct the URL to the Flask server that serves the files
            
            return FileResponse(path=f'{cover_image_data["relative_base_path"]}{cover_image_data["cover_filename"]}', media_type='image/jpeg')            
        else:
            # Return URL to a default no cover image
            logger.error('No cover image found in the database.')
            return {"url": "http://your-flask-domain.com/static/no_cover.jpg"}
    except Exception as e:
        logger.error(f"Error fetching cover image: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get('/serve_books', tags=["books"])
async def serve_books():
    try:
        books_fetcher = FetchBooksFromDB() 
        books = await books_fetcher.fetch_books_from_database()
        return books  

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get('/fetch_book_details_by_id/{id}', tags=["books"])
async def fetch_book_details(id):
    try:
        book_fetcher = FetchBookDetailsFromDB()
        book = book_fetcher.fetch_book_details_by_id(id)  
        logger.info(book)
        return (book)
    except Exception as e:
        logger.error(f"Error fetching book details: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    