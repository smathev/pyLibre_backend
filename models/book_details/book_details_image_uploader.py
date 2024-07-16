import os
import shutil
import re
from werkzeug.utils import secure_filename  # Update import statement
from db.fetch_data_operations import FetchBookDetailsFromDB
from models.utils_path_manager import path_manager

from loguru import logger

temp_image_folder = path_manager.temp_image_folder_full_path
library_folder = path_manager.library_folder_full_path


class ImageUploader:
    def __init__(self, id, file):
        self.file = file
        self.id = id

    def upload_image_temp(self, file, id):
        try:
            original_filename = secure_filename(file.filename)
            _, file_extension = os.path.splitext(original_filename)
            new_filename = f"{id}{file_extension}"
            temp_filepath = os.path.join(temp_image_folder, new_filename)
            # Check if the file already exists
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)  # Remove the existing file
            file.save(temp_filepath)
            return new_filename
        except Exception as e:
            # Log the exception details here
            logger.error(f"Error saving temporary file: {e}")
            return None

    def construct_file_path(self, book_path, title):
        try:
            # Remove characters that are not suitable for a file path
            title = re.sub(r'[^\w\s-]', '', title.strip())
            file_path = os.path.join(book_path, f"{title}.jpg")
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            return file_path
        except Exception as e:
            # Log the exception details here
            logger.error(f"Error constructing file path: {e}")
            return None
    
    def make_image_permanent(self, id):
        try:
            # Get the book details from the database
            temp_image_filename = os.path.join(temp_image_folder, f"{id}.jpg")
            book_fetcher = FetchBookDetailsFromDB()
            book = book_fetcher.fetch_book_details_by_id(self.id)
            if not book:
                logger.warning(f"No book found with UUID: {self.id}")
                return None
            title = book['title']
            book_path = book['full_base_path']
            file_path = self.construct_file_path(book_path, title)
                       
            if file_path is None:
                logger.warning("Failed to construct a valid file path.")
                return None

            # Move the file from the temp folder to the permanent location
            shutil.move(temp_image_filename, file_path)
            return file_path
        except FileNotFoundError:
            logger.warning(f"Temporary file not found at {temp_image_filename}.")
            return None
        except Exception as e:
            # Log the exception details here
            logger.error(f"Error making image permanent: {e}")
            return None

    def remove_image_temp(self, id):
        try:
            temp_image_filename = os.path.join(temp_image_folder, f"{id}.jpg")
            os.remove(temp_image_filename)
            return temp_image_filename
        except FileNotFoundError:
            logger.warning(f"Temporary file not found at {temp_image_filename}.")
            return None
        except Exception as e:
            # Log the exception details here
            logger.error(f"Error making image permanent: {e}")
            return None