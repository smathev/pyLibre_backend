from db.db_book_update_book_metadata_by_id import UpdateBookMetadataByID

from loguru import logger

class SaveBookDetailsDB:
    def save_details_to_db(self, id, data):
        update_db = UpdateBookMetadataByID()
        try:
            # Assuming 'data' is passed in JSON format in the request body
            update_db.update_book_metadata_by_id(id, data)
        except Exception as e:
            logger.error(f'ERROR when saving book details to DB: {e}')

        