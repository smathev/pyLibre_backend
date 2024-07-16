from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from db.fetch_data_operations import FetchShelvesAndBooksOnShelves
from db.edit_shelves import CreateNewShelf, RemoveBookFromShelf, AddBookToShelf

from db.db_sync_methods import ShelvesChangeShouldSyncStatus

router = APIRouter()

@router.get('/shelves/fetch_shelves_and_book_shelf_links', tags=["shelves"])
def fetch_shelves_and_books():
    try:
        shelves_and_book_shelf_links_fetcher = FetchShelvesAndBooksOnShelves() 
        shelves = shelves_and_book_shelf_links_fetcher.fetch_shelves_and_books()
        return shelves  

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/shelves/serve_shelves', tags=["shelves"])
def serve_shelves():
    try:
        shelves_and_book_shelf_links_fetcher = FetchShelvesAndBooksOnShelves() 
        shelves = shelves_and_book_shelf_links_fetcher.fetch_shelves_and_books()
        return shelves  

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/shelves/create_new_shelf', tags=["shelves"])
async def create_new_shelf(request: Request):
    try:
        data = await request.json()
        shelf_name = data['shelf_name']
        shelf_creator = CreateNewShelf() 
        new_shelf = shelf_creator.create_new_shelf(shelf_name)
        return new_shelf  

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/shelves/add_book_to_shelf/{shelf_id}', tags=["shelves"])
async def add_book_to_shelf(shelf_id: int, request: Request):
    try:
        data = await request.json()
        book_id = data['book_id']
        add_book_to_shelf_processor = AddBookToShelf() 
        book_status = add_book_to_shelf_processor.add_book_to_shelf(book_id, shelf_id)   
        return book_status  

    except Exception as e:
        logger.error(f"Error adding book to shelf: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/shelves/remove_book_from_shelf/{shelf_id}', tags=["shelves"])
async def remove_book_to_shelf(shelf_id: int, request: Request):
    try:
        data = await request.json()
        book_id = data['book_id']
        remove_book_from_shelf_processor = RemoveBookFromShelf() 
        book_status = remove_book_from_shelf_processor.remove_book_from_shelf(book_id, shelf_id)
        return book_status  

    except Exception as e:
        logger.error(f"Error removing book from shelf: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/shelves/create_new_shelf', tags=["shelves"])
def remove_book_to_shelf(shelf_name: str):
    try:
        shelves_and_book_shelf_links_fetcher = FetchShelvesAndBooksOnShelves() 
        shelves = shelves_and_book_shelf_links_fetcher.fetch_shelves_and_books()
        return shelves  

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/shelves/delete_shelf', tags=["shelves"])
def remove_book_to_shelf(shelf_id: int):
    try:
        shelves_and_book_shelf_links_fetcher = FetchShelvesAndBooksOnShelves() 
        shelves = shelves_and_book_shelf_links_fetcher.fetch_shelves_and_books()
        return shelves  

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/shelves/set_sync_status_for_shelf/{shelf_id}', tags=["shelves"])
async def set_sync_status_for_shelf_and_books(shelf_id: int, request: Request):
    try:

        data = await request.json()
        logger.info(f"Received data: {data}")  # Log the incoming data
        should_sync = data['should_sync']
        setSyncStatusOnShelf_processor = ShelvesChangeShouldSyncStatus() 
        result = setSyncStatusOnShelf_processor.update_shelf_should_sync(shelf_id, should_sync)
        return result  
    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=str(e))