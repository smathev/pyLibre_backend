from db.fetch_data_operations import FetchBookDetailsFromDB
import os
import shutil
from loguru import logger

class MoveFilesWhenUpdatingTitleOrAuthor:
    def move_files_when_updating_titleORAuthor(self, id, new_paths):
        try:
            logger.info(f"Will move file {new_paths['epub_filename']} due to update in title OR author")
            # Assuming 'data' is passed in JSON format in the request body
            book_fetcher = FetchBookDetailsFromDB()
            book_data = book_fetcher.fetch_book_details_by_id(id)
            previous_complete_path_from_db=book_data['full_base_path']
            previous_epub_filename_from_db=book_data['epub_filename']
            previous_cover_image_filename_from_db = book_data['cover_filename']
            previous_full_path_epub = os.path.join(previous_complete_path_from_db, previous_epub_filename_from_db)
            previous_full_path_cover = os.path.join(previous_complete_path_from_db, previous_cover_image_filename_from_db)
            new_complete_path=new_paths['full_base_path']
            new_epub_filename=new_paths['epub_filename']
            new_cover_image_filename = new_paths['cover_filename']
            new_full_path_epub = os.path.join(new_complete_path, new_epub_filename)
            new_full_path_cover = os.path.join(new_complete_path, new_cover_image_filename)
            if not os.path.exists(new_complete_path):
                os.makedirs(new_complete_path)
                logger.info(f"Created new folder: {new_complete_path}")
            shutil.move(previous_full_path_epub, new_full_path_epub)
            shutil.move(previous_full_path_cover, new_full_path_cover)
            if os.path.exists(previous_complete_path_from_db):
                os.rmdir(previous_complete_path_from_db)
            logger.info(f"successfully moved {new_paths['epub_filename']} to {new_full_path_epub}")
            logger.info(f"successfully moved {new_paths['cover_filename']} to {new_cover_image_filename}")
            return new_full_path_epub, new_full_path_cover            
        except Exception as e:
            logger.error(f'Moving file due to title OR author update failed: {e}')

        
