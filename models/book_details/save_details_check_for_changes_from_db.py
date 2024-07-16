from db.fetch_data_operations import FetchBookDetailsFromDB
from loguru import logger

class SaveDetailsCheckForChanges:
    def check_details_for_changes(self, id, data):
        book_fetcher = FetchBookDetailsFromDB()
        try:
            book_from_db = book_fetcher.fetch_book_details_by_id(id)
            book_from_db_json = {
                'title': book_from_db.get('title', ''),
                'isbn': book_from_db.get('isbn', ''),
                'genre': book_from_db.get('genre', ''),
                'description': book_from_db.get('description', ''),
                'series_titles': book_from_db.get('series_titles', ''),
                'number_in_series': book_from_db.get('number_in_series', '')
            }
            logger.debug(f"Fetched from DB: {book_from_db_json}")

            incoming_data_json = {key: data.get(key, '') for key in book_from_db_json.keys()}  # Ensure we only use relevant keys
            logger.debug(f"Incoming Data: {incoming_data_json}")

            changes_in_data = {key: incoming_data_json[key] for key in incoming_data_json if incoming_data_json[key] != book_from_db_json[key]}
            logger.info(f"Detected Changes: {changes_in_data}")

            return changes_in_data

        except Exception as e:
            logger.error(f"Error when checking for changes: {e}")
            raise 