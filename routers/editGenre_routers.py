from fastapi import APIRouter, HTTPException
from loguru import logger
from db.edit_authors_in_books import EditAuthorsInBook
from models.book_details.save_details_main import BookDetailUpdater

from db.db_crud_methods import UpdateBook_SingleItem
from db.edit_genres_in_books import EditGenresInBook  # Assuming this module handles genre-related DB operations

from sqlalchemy.exc import SQLAlchemyError
from schemas.response_model import ResponseModel
from schemas.book_details import (BookDetails,
                                  AddDeleteAuthorSchema,
                                  UpdateBookTitle, 
                                  UpdateBookMetadata,
                                  AddDeleteAuthorResponse)

# Import the genre-related schemas
from schemas.genre_details import (GenreDetails,
                                   AddDeleteGenreSchema,
                                   UpdateGenreName,
                                   GenreDetailsResponse,
                                   AddDeleteGenreResponse,
                                   UpdateGenreNameResponse)

router = APIRouter()

update_book_metadata_single_item = UpdateBook_SingleItem()

edit_book_authors_processor = EditAuthorsInBook()

edit_book_genres_processor = EditGenresInBook()  # Assuming this is the processor for genres

save_all_details_processor = BookDetailUpdater()

# Existing routes...
# TODO Create actual DB_functions to add, delete, change genres and add or remove genres from books
# New routes for genres

# Add a new genre to the system
@router.post('/genres/add', response_model=AddDeleteGenreResponse, status_code=200, description="Add a new genre", summary="Add a new genre", tags=["Genres"])
async def add_genre(genre_details: GenreDetails):
    try:
        result = await edit_book_genres_processor.add_genre(genre_details)
        logger.info(result)
        return AddDeleteGenreResponse(status="success", message="Genre added successfully", data={"genre_name": genre_details.genre_name})
    except Exception as e:
        logger.error(f"Error adding genre: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Delete a genre from the system
@router.delete('/genres/{genre_id}/delete', response_model=AddDeleteGenreResponse, status_code=200, description="Delete a genre", summary="Delete a genre", tags=["Genres"])
async def delete_genre(genre_id: int):
    try:
        result = await edit_book_genres_processor.delete_genre(genre_id)
        logger.info(result)
        return AddDeleteGenreResponse(status="success", message="Genre deleted successfully", data={"genre_id": genre_id})
    except Exception as e:
        logger.error(f"Error deleting genre: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Add a genre to a book
@router.post('/edit_book/{book_id}/add_genre_to_book/{genre_id}', response_model=AddDeleteGenreResponse, status_code=200, description="Add a genre to a book", summary="Add a genre to a book", tags=["Edit Book"])
async def add_genre_to_book(book_id: int, genre_id: int, genre_update_schema: AddDeleteGenreSchema):
    try:
        # Update the schema with the path parameters to ensure consistency
        genre_update_schema.book_id = book_id
        genre_update_schema.genre_id = genre_id

        result = await edit_book_genres_processor.add_genre_to_book(genre_update_schema)
        logger.info(result)
        return AddDeleteGenreResponse(status="success", message="Genre added to book successfully", data={"book_id": book_id, "genre_id": genre_id})
    except Exception as e:
        logger.error(f"Error adding genre to book: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Remove a genre from a book
@router.delete('/edit_book/{book_id}/remove_genre_from_book/{genre_id}', response_model=AddDeleteGenreResponse, status_code=200, description="Remove a genre from a book", summary="Remove a genre from a book", tags=["Edit Book"])
async def remove_genre_from_book(book_id: int, genre_id: int, genre_update_schema: AddDeleteGenreSchema):
    try:
        # Update the schema with the path parameters to ensure consistency
        genre_update_schema.book_id = book_id
        genre_update_schema.genre_id = genre_id

        result = await edit_book_genres_processor.remove_genre_from_book(genre_update_schema)
        logger.info(result)
        return AddDeleteGenreResponse(status="success", message="Genre removed from book successfully", data={"book_id": book_id, "genre_id": genre_id})
    except Exception as e:
        logger.error(f"Error removing genre from book: {e}")
        raise HTTPException(status_code=500, detail=str(e))
