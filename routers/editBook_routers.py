from fastapi import APIRouter, HTTPException
from loguru import logger
from db.edit_authors_in_books import EditAuthorsInBook
from models.book_details.save_details_main import BookDetailUpdater

from db.db_crud_methods import UpdateBook_SingleItem

from sqlalchemy.exc import SQLAlchemyError
from schemas.response_model import ResponseModel
from schemas.book_details import (BookDetails,
                                  AddDeleteAuthorSchema,
                                  UpdateBookTitle, 
                                  UpdateBookMetadata,
                                  AddDeleteAuthorResponse)


router = APIRouter()

update_book_metadata_single_item = UpdateBook_SingleItem()

edit_book_authors_processor = EditAuthorsInBook()

save_all_details_processor = BookDetailUpdater()

@router.post('/edit_book/add_author_to_book/', response_model=AddDeleteAuthorResponse, status_code=200, description="Add an author to a book", summary="Add an author to a book", tags=["Edit Book"])
async def add_author_to_book(author_update_schema: AddDeleteAuthorSchema): #, book_id: int, author_id: int):
    try:
        #result = await edit_book_authors_processor.add_author_to_book(book_id, author_id)
        result = await edit_book_authors_processor.add_author_to_book(author_update_schema)
        logger.info(result)
        return AddDeleteAuthorResponse(status="success", message="Author added successfully", data=author_update_schema)
    except Exception as e:
        logger.error(f"Error deleting author from book: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/edit_book/{book_id}/delete_author_from_book/{author_id}', response_model=ResponseModel, status_code=200, description="Delete an author from a book", summary="Delete an author from a book", tags=["Edit Book"])
async def delete_author_from_book(author_update_schema: AddDeleteAuthorSchema): #, book_id: int, author_id: int):
    try:
        #result = await edit_book_authors_processor.delete_author_from_book(book_id, author_id)
        result = await edit_book_authors_processor.delete_author_from_book(author_update_schema)
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"Error deleting author from book: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/edit_book/{book_id}/save_all_details', response_model=ResponseModel, status_code=200, description="Save all details of a book", summary="Save all details of a book", tags=["Edit Book"])
async def save_all_details(book_id: int, new_details: BookDetails):
    try:
        # Assuming save_all_details_processor.process_changes_update_accordingly accepts a Pydantic model
        result = save_all_details_processor.process_changes_update_accordingly(book_id, new_details.dict())
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"Error saving book details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/edit_book/{book_id}/change_title', response_model=ResponseModel, status_code=200, description="Change the title of a book", summary="Change the title of a book", tags=["Edit Book"])
async def change_title_of_book(update_book_metadata: UpdateBookMetadata):
    try:
        new_title = update_book_metadata.new_string
        column_to_update = 'title'
        book_id = update_book_metadata.book_id
        result = update_book_metadata_single_item.update_single_metadata_item_book(book_id, column_to_update, new_title )
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"Error updating title of book: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post('/edit_book/{book_id}/change_ISBN/{isbn}', response_model=ResponseModel, status_code=200, description="Change the ISBN of a book", summary="Change the ISBN of a book", tags=["unused"])
async def change_isbn_in_book(update_book_metadata: UpdateBookMetadata):
    try:
        new_isbn = update_book_metadata.new_string
        column_to_update = 'isbn'
        book_id = update_book_metadata.book_id
        result = update_book_metadata_single_item.update_single_metadata_item_book(book_id, column_to_update, new_isbn )
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"Error updating ISBN of book: {e}")
        raise HTTPException(status_code=500, detail=str(e))

########################### UNUSED might need to use later, if it's easier to individually update the records #######################################



@router.post('/edit_book/{book_id}/add_genre/{genre}',  response_model=ResponseModel, status_code=200, description="Add a genre to a book", summary="Add a genre to a book", tags=["unused"])
async def add_genre_to_book(book_id: int, genre: str):
    pass  # Implement your logic here

@router.post('/edit_book/{book_id}/delete_genre/{genre}', response_model=ResponseModel, status_code=200, description="Delete a genre from a book", summary="Delete a genre from a book", tags=["unused"])
async def delete_genre_from_book(book_id: int, genre: str):
    pass  # Implement your logic here

@router.post('/edit_book/{book_id}/change_description', response_model=ResponseModel, status_code=200, description="Change the description of a book", summary="Change the description of a book", tags=["unused"])
async def change_description_of_book(book_id: int, description: str):
    pass  # Implement your logic here

@router.post('/edit_book/{book_id}/add_book_to_series/{book_series}',  response_model=ResponseModel, status_code=200, description="Add a book to a series", summary="Add a book to a series", tags=["unused"])
async def add_book_to_series(book_id: int, book_series: str):
    pass  # Implement your logic here

@router.post('/edit_book/{book_id}/delete_book_from_series/{book_series}', response_model=ResponseModel, status_code=200, description="Delete a book from a series", summary="Delete a book from a series", tags=["unused"])
async def delete_book_from_series(book_id: int, book_series: str):
    pass  # Implement your logic here

@router.post('/edit_book/{book_id}/{series_id}/change_book_number_in_series/{number_in_series}', response_model=ResponseModel, status_code=200, description="Change the number of a book in a series", summary="Change the number of a book in a series", tags=["unused"])
async def change_book_number_in_series(book_id: int, series_id: int, number_in_series: int):
    pass  # Implement your logic here

