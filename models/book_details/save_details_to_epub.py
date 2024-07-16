from db.fetch_data_operations import FetchBookDetailsFromDB
from models.epub.epub_update_metadata_in_epub import SaveDetailsToEpubMetadataFile
from loguru import logger

import os
import ebooklib
from ebooklib import epub

class SaveDetailsToEpubMetadata:
    def save_details_to_epub_metadata(self, id, data):
        book_fetcher = FetchBookDetailsFromDB()
        epub_updater = SaveDetailsToEpubMetadataFile()
        try:
            # Fetch book details from the database
            book_from_db = book_fetcher.fetch_book_details_by_id(id)
            epub_filename = os.path.join(book_from_db.get('full_base_path', ''), book_from_db.get('epub_filename', ''))
            result = epub_updater.save_details_to_epub_metadata(epub_filename, data)
            logger.info(f"Updated metadata in EPUB: {result}")
            return result
        except Exception as e:
            logger.error(f"Error when updating metadata in EPUB: {e}")