from schemas.endpoint_search_query_schema import Book, ResponseModel as search_response_model
from db.classDefinitions.book_series import BookSeries
from db.classDefinitions.author import Author
from db.db_manager.sync_db_manager import SyncDBManager
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.book_shelf_links import BookShelfLinks
from loguru import logger
from sqlalchemy.sql import text

class SearchForAuthor(SyncDBManager):
    def __init__(self):
        super().__init__()

    def search_for_authors(self, query):
        try:
            with self.Session() as session:
                if len(query) < 3:
                    return []  # Return empty list if query is too short

                # Corrected query to use session.query(Author)
                authors = session.query(Author).filter(Author.name.ilike(f'%{query}%')).all()
                author_data = [{'id': author.id, 'name': author.name} for author in authors]
                return author_data
        except Exception as e:
            logger.error(f"Error searching for author with search term: {query} Exception: {e}")
            return None

class FTSSearchForBooks(SyncDBManager):
    def __init__(self):
        super().__init__()

    def fts_search_ebooks(self, query):
        try:
            with self.Session() as session:
                # Prepare the search query for FTS MATCH
                modified_query = f"*{query}*" if query else query  # Assuming wildcard usage for partial matches
                # Use the MATCH clause properly in the SQL query
                results = session.execute(
                    text("SELECT rowid, title, authors FROM book_fts WHERE book_fts MATCH :query LIMIT 15"),
                    {'query': modified_query}  # Use the modified_query variable instead of a hardcoded value
                ).fetchall()

                # Convert the results to a list of dictionaries
                results_dict = [{'id': row[0], 'title': row[1], 'authors': row[2]} for row in results]  # Access tuple values by integer indices

                logger.debug(f"Results: {results_dict}")

                books = [Book(id=result['id'], title=result['title'], authors=result['authors']) for result in results_dict]
                return search_response_model(results=books)
        except Exception as e:
            logger.error(f"Error performing FTS search for books: {e}")
            return []
        
class SearchQueryForShelvesWithoutBook(SyncDBManager):
    def search_query_for_shelves_without_book(self, search_term, book_id):
        try:
            with self.Session() as session:
                # Fetch shelves that do not have the current book
                subquery = (
                    session.query(BookShelfLinks.shelf_id)
                    .filter(BookShelfLinks.book_id == book_id)
                    .subquery()
                )
                
                shelves = (
                    session.query(Shelf)
                    .filter(Shelf.shelf_name == search_term)
                    .filter(Shelf.id.notin_(subquery))
                    .all()
                )

                shelves_data = []
                for shelf in shelves:
                    shelf_data = {
                        "id": shelf.id,
                        "shelf_name": shelf.shelf_name,
                        "uuid": shelf.uuid,
                        "kobo_should_sync": shelf.kobo_should_sync,
                        "date_added": shelf.date_added,
                        "date_updated": shelf.date_updated,
                        "books": []  # Placeholder for books
                    }
                    shelves_data.append(shelf_data)

                return shelves_data

        except Exception as e:
            logger.error(f"Error fetching shelves without book: {e}")
            return None

class SearchQueryForSeries(SyncDBManager):
    def __init__(self):
        super().__init__()

    def search_for_series_in_series_table(self, query):
        try:
            with self.Session() as session:
                # Modify the query to add a wildcard for partial matches
                modified_query = f"%{query}%"

                # Execute the query using SQLAlchemy
                results = session.query(BookSeries.series_title).filter(BookSeries.series_title.like(modified_query)).limit(15).all()
                
                # Convert the results to a list of dictionaries
                results_dict = [{'series': row[0]} for row in results]

                logger.debug(f"Results: {results_dict}")

                return results_dict
        except Exception as e:
            logger.error(f"Error searching for series: {e}")
            return []
