import os
from loguru import logger
from models.utils_path_manager import path_manager
from models.clean_folder_and_file_name import CleanFolderAndFileName
import shutil

class ePubMover:
    def __init__(self):
        self.library_folder = path_manager.library_folder_full_path
        self.clean_names = CleanFolderAndFileName()

    def metadata_update(self, metadata, metadata_is_none, filename=None, relative_directory_path=None, complete_path=None):
        if metadata_is_none:
            metadata.update({
                'filename': None,
                'relative_directory_path': None,
                'complete_path': None
            })
        else:            
            metadata.update({
                'filename': filename,
                'relative_directory_path': relative_directory_path,
                'complete_path': complete_path
            })

    def move_epub_based_on_metadata(self, original_file_path, metadata):
        try:
            creator = metadata.get('creator')
            title = metadata.get('title')
            
            metadata_is_none = False  # Flag to check if metadata should be set to None
            
            if not creator or not title:
                logger.error("Creator or title missing in metadata")
                logger.debug(f"Metadata: {metadata}")  # Log the metadata for debugging
                metadata_is_none = True
            folder_creator = self.clean_names.clean_string_for_OS_illegal_characters(creator)
            file_title = self.clean_names.clean_string_for_OS_illegal_characters(title)
            destination_folder = os.path.join(self.library_folder, folder_creator, file_title)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
                logger.info(f"Created new folder: {destination_folder}")
            
            relative_base_path = os.path.relpath(destination_folder, self.library_folder)
            filename = os.path.basename(original_file_path)
            relative_directory_path = os.path.join('books', relative_base_path, '').replace('\\', '/')
            complete_path = os.path.join(destination_folder, '').replace('\\', '/')
            complete_file_path = os.path.join(destination_folder, filename)

            if os.path.exists(complete_file_path):
                logger.error(f"EPUB file already in file_path: {complete_file_path}")
                metadata_is_none = True

            else:
                shutil.copy(original_file_path, destination_folder)
                logger.info(f"Moved EPUB file to library: {complete_path}")

            self.metadata_update(metadata, metadata_is_none, filename, relative_directory_path, complete_path)
            return metadata

        except Exception as e:
            logger.error(f"Error moving EPUB file to library: {e}")
            self.metadata_update(metadata, True)
            return metadata