from db.fetch_data_operations import FetchBookDetailsFromDB
from models.utils_path_manager import path_manager
import os

from loguru import logger

from models.clean_folder_and_file_name import CleanFolderAndFileName

class GenerateNewFilenames:
    def __init__(self):
        self.library_folder = path_manager.library_folder_full_path

    def new_filenames_when_updating_titleORauthor(self, id, changes_in_data):
        book_fetcher = FetchBookDetailsFromDB()
        book_data = book_fetcher.fetch_book_details_by_id(id)
        string_cleaner = CleanFolderAndFileName()   
        
        new_paths = {}
        try:
            if 'title' in changes_in_data:
                title = changes_in_data['title']
                new_cover_image_filename = f'{title}.jpg'
                new_epub_filename = f'{title}.epub'
                new_paths.update({'cover_filename': new_cover_image_filename, 'epub_filename': new_epub_filename})
                logger.info(f"Changing title from {book_data['title']} to {title}")
            else:
                title = book_data['title']
                cover_file_name = string_cleaner.clean_string_for_OS_illegal_characters(book_data['cover_filename'])
                epub_filename = string_cleaner.clean_string_for_OS_illegal_characters(book_data['epub_filename'])
                new_paths.update({'cover_filename': cover_file_name, 'epub_filename': epub_filename})
            if 'author' in changes_in_data:
                author = changes_in_data['author']
                logger.info(f"Changing author from {book_data['author']} to {author}")
                author = string_cleaner.clean_string_for_OS_illegal_characters(author)
            else:
                author = book_data['author']
            title = string_cleaner.clean_string_for_OS_illegal_characters(title)
            complete_path = os.path.join(self.library_folder, author, title)
            relative_base_path = os.path.relpath(complete_path, self.library_folder)
            relative_directory_path = os.path.join('books', relative_base_path, '').replace('\\', '/')
            new_complete_path = os.path.join(complete_path, '').replace('\\', '/')
            new_paths.update({'full_base_path': new_complete_path, 'relative_base_path': relative_directory_path})
            logger.info(f"Changing author from {book_data['author']} to {author}")
            return new_paths
        except Exception as e:
            logger.error(f'Creating new file_paths failed: {e}')