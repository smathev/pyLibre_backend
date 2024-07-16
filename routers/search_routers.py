from fastapi import APIRouter, HTTPException
from loguru import logger
from db.db_search_for_data_operations import FTSSearchForBooks
from schemas.endpoint_search_query_schema import SearchQuery, ResponseModel 

from db.db_search_for_data_operations import SearchForAuthor, SearchQueryForShelvesWithoutBook, SearchQueryForSeries

from loguru import logger
router = APIRouter()

@router.post('/search/search_for_books', response_model=ResponseModel, tags=["search"])
def search_for_books(search_query: SearchQuery):
    try:
        db_fts_books_search = FTSSearchForBooks()
        logger.info(f"query: {search_query}")
        query = search_query.search_query
        results = db_fts_books_search.fts_search_ebooks(query)  # Ensure this method returns necessary fields
        return results
    except Exception as e:
        logger.error(f"Error searching for book: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/search/search_for_authors', tags=["search"])
def search_for_authors(search_query: str):
    try:
        search_for_authors_processor = SearchForAuthor()
        logger.info(f"query: {search_query}")
        results = search_for_authors_processor.search_for_authors(search_query)  # Ensure this method returns necessary fields
        return (results)
    except Exception as e:
        logger.error(f"Error searching for author: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/shelves/search_for_shelves', tags=["search"])
def search_shelves(search_query: SearchQuery):
    search_term = search_query.search_query
    book_id = search_query.id

    suggestions = SearchQueryForShelvesWithoutBook().search_query_for_shelves_without_book(search_term, book_id)
    
    return ({'suggestions': suggestions})

@router.post('/series/search_for_series', tags=["search"])
def search_shelves(search_query: SearchQuery):
    search_term = search_query.search_query
    
    results = SearchQueryForSeries().search_for_series_in_series_table(search_term)
    
    return (results)