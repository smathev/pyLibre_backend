import os
import ebooklib
from ebooklib import epub

class SaveDetailsToEpubMetadataFile:
    def save_details_to_epub_metadata(self, epub_filename, data):
        epub_book = epub.read_epub(epub_filename)
        # Dictionary to map keys to methods
        method_mapping = {
            'title': epub_book.set_title,
            'author': epub_book.add_author,
            'language': epub_book.set_language,
            'identifier': epub_book.set_identifier,
            'cover': epub_book.set_cover
        }

        # Access the metadata_changes sub-object
        metadata_changes = data.get('metadata_changes', {})

        # Iterate over keys and values of metadata_changes
        for key, value in metadata_changes.items():
            if key in method_mapping:
                method = method_mapping[key]
                method(value)
        
        # Save the book after updating metadata
        result = epub.write_epub(epub_filename, epub_book)
        return result