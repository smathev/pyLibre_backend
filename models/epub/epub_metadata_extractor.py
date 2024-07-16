import re
from ebooklib import epub
from schemas.epub_schema import EpubDCMetadata
from loguru import logger

# Set up logging

class EpubMetadataExtractor:
    @staticmethod
    def extract_epub_metadata(file_path):
        try:
            # Try to read the EPUB file
            book = epub.read_epub(file_path)
            logger.info(f"Successfully read EPUB file: {file_path}")
        except Exception as e:
            logger.error(f"Error reading EPUB file {file_path}: {e}")
            return None

        metadata = {}
        unmapped_fields = []
        metadata_startingobject = EpubDCMetadata.__fields__.items()
        counter_creator = 0  # Initialize the counter here
        counter_contributor = 0  # Initialize the counter here

        try:
            for variable, field in EpubDCMetadata.__fields__.items():
                dc_metadata = book.get_metadata('DC', field.alias)
                if dc_metadata:
                    value = dc_metadata[0][0] if dc_metadata[0][0] else None
                    if variable == 'identifier':
                        value = EpubMetadataExtractor.extract_isbn_from_identifier(value)
                    if variable == 'creator':
                        counter_creator += 1  # Increment the counter for each creator found
                        if counter_creator > 1:
                            logger.error(f"field: {variable}, contents: {value}. Counter_creator is above {counter_creator} for {file_path}")
                    if variable == 'contributor':
                        counter_contributor += 1  # Increment the counter for each creator found
                        if counter_contributor > 1:
                            logger.error(f"field: {variable}, contents: {value}. Counter_contributor is above {counter_contributor} for {file_path}")
                    metadata[variable] = value
                else:
                    unmapped_fields.append(variable)

            if unmapped_fields:
                logger.info(f"The following metadata fields could not be mapped to the EpubDCMetadata schema: {unmapped_fields}")

            logger.info(f"Metadata extracted from EPUB file {file_path}: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from EPUB file {file_path}: {e}")
            return None

    @staticmethod
    def extract_isbn_from_identifier(identifier):
        try:
            isbn_match = re.search(r'ISBN:(\d+)', identifier)
            if isbn_match:
                isbn = isbn_match.group(1)
                if len(isbn) == 10 or len(isbn) == 13:
                    return isbn
            return None
        except Exception as e:
            logger.error(f"Error extracting ISBN from identifier: {e}")
            return None