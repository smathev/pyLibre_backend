from models.epub.epub_metadata_extractor import EpubMetadataExtractor
from models.utils_path_manager import path_manager

from loguru import logger

class EpubProcessor:
    def __init__(self):
        self.library_folder = path_manager.library_folder_full_path

    def process_epub_files(self, epub_file):
            try:
                metadata = EpubMetadataExtractor.extract_epub_metadata(epub_file)
                logger.info(f"Extracted metadata from EPUB: {metadata}")
                return metadata
            except Exception as e:
                logger.error(f"Error processing EPUB file '{epub_file}': {e}")

