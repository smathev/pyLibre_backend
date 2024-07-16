import os
from models.utils_path_manager import path_manager
from db.fetch_data_operations import FetchBookDetailsFromDB
from models.clean_folder_and_file_name import CleanFolderAndFileName
import shutil

class FileManager:
    def __init__(self):
        self.library_folder = path_manager.library_folder_full_path    
        self.path_cleaner = CleanFolderAndFileName.clean_string_for_OS_illegal_characters()

    @staticmethod
    def get_current_file_paths(book_id):
        book_fetcher = FetchBookDetailsFromDB()
        book_data = book_fetcher.fetch_book_details_by_id(book_id)
        current_complete_path_from_db = book_data['full_base_path']
        current_epub_filename_from_db = book_data['epub_filename']
        current_cover_image_filename_from_db = book_data['cover_filename']
        current_full_path_epub = os.path.join(current_complete_path_from_db, current_epub_filename_from_db)
        current_full_path_cover = os.path.join(current_complete_path_from_db, current_cover_image_filename_from_db)
        current_paths = {
            'current_full_path_epub': current_full_path_epub,
            'current_full_path_cover': current_full_path_cover
        }
        return current_paths

    def create_new_file_paths(self, author_name, book_title):
        new_file_path = author_name + '/' + book_title + '/'
        new_epub_filename = f"{book_title}.epub"
        new_cover_filename = f"{book_title}.jpg"
        full_epub_path = self.library_folder + new_file_path + new_epub_filename
        clean_epub_path = self.path_cleaner(full_epub_path)
        full_cover_path = self.library_folder + new_file_path + new_cover_filename
        clean_cover_path = self.path_cleaner(full_cover_path)
        new_paths = {
            'full_epub_path': clean_epub_path,
            'full_cover_path': clean_cover_path
        }
        return new_paths

    @staticmethod
    def move_file(source, destination):
        if not os.path.exists(destination):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(source, destination)