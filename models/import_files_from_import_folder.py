from models.scan_import_folder import ImportFolderScanner

from models.metadata_map_to_book_schema import MetadataMapToBook

from db.db_book_insert_new_book_metadata import InsertNewBookMetadata
from db.db_book_update_book_metadata_by_id import UpdateBookMetadataByID

from models.epub.process_epub_files import EpubProcessor
from models.epub.move_epub_from_import_to_library_folder import ePubMover
from models.epub.extract_epub_cover_image_to_epub_folder import EpubCoverExtractor

from models.utils_path_manager import path_manager  
from loguru import logger

import os


class FileImporter:
    def __init__(self):
        logger.info("FileImporter initialized")
        self.book_insert_new_data = InsertNewBookMetadata()
        self.book_update_book_metadata = UpdateBookMetadataByID()
        self.library_folder = path_manager.library_folder_full_path

    def get_supported_files_from_import_folder(self):
        try:
            folderscanner = ImportFolderScanner()
            supported_files_found = folderscanner.get_relevant_files_in_import_folder()
            logger.info(f"Found {len(supported_files_found)} supported files")
            return supported_files_found
        except Exception as e:
            logger.error(f"failed to get all supported files: {e}")
            raise

    def get_metadata_from_epub_file(self, file):
        try:
            processor = EpubProcessor()
            metadata = processor.process_epub_files(file)
            return metadata
        except Exception as e:
            logger.error(f"failed to get metadata from epub file: {e}")
            raise

    def map_metadata_from_file_to_book_schema(self, metadata):
        try:
            map_metadata_to_book_schema = MetadataMapToBook()
            metadata = map_metadata_to_book_schema.map_metadata_to_book(metadata)
            return metadata
        except Exception as e:
            logger.error(f"failed to map metadata to book_schema: {e}")
            raise
    
    def input_metadata_to_database(self, mapped_book):
        try:
            uuid = self.book_insert_new_data.insert_new_book_metadata(dict(mapped_book))
            return uuid
        except Exception as e:
            logger.error(f"failed to input mapped metadata to database: {e}")
            raise

    def move_book_from_import_to_library_folder(self, import_path, metadata):
        logger.info(f"Moving {import_path} to books folder...")
        book_mover = ePubMover()
        metadata = book_mover.move_epub_based_on_metadata(import_path, metadata)
        return metadata
    
    def extract_cover_image_and_place_in_library_folder(self, metadata):
        cover_extractor = EpubCoverExtractor()
        metadata = cover_extractor.extract_cover(metadata)
        return metadata

    def check_if_cover_image_exists(self, output_image_path):        
        if os.path.exists(output_image_path):
            return True
        return False

    def process_all_imported_files(self):
        supported_files = self.get_supported_files_from_import_folder()
        logger.info(f"Processing {len(supported_files)} files...")
        for file in supported_files:
            try:
                logger.info(f"Processing file: {file}")
                metadata = self.get_metadata_from_epub_file(file)                
                metadata = self.move_book_from_import_to_library_folder(file, metadata)
                metadata = self.extract_cover_image_and_place_in_library_folder(metadata)
                mapped_book = self.map_metadata_from_file_to_book_schema(metadata)
                id = self.input_metadata_to_database(mapped_book)
            except Exception as e:
                logger.error(f"Error processing file {file}: {e}")
                continue
