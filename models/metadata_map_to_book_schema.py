from schemas.book_schema import BookSchema
from loguru import logger



class MetadataMapToBook:
    @staticmethod
    def map_metadata_to_book(metadata):
        try:
            common_fields = {
                'isbn': metadata.get('identifier'),
                'title': metadata.get('title'),
                'author': metadata.get('creator'),
                'publisher': metadata.get('publisher'),
                'publication_date': metadata.get('date'),
                'year': metadata.get('year'),
                'language': metadata.get('language'),
                'description': metadata.get('description'),
                'relative_base_path': metadata.get('relative_directory_path'),
                'full_base_path': metadata.get('complete_path'),
                'epub_filename': metadata.get('filename'),
                'cover_filename': metadata.get('cover_filename')
            }

            book_data = {}
            for field_name, field_value in common_fields.items():
                book_data[field_name] = field_value

            book = BookSchema(**book_data)
            logger.info(f"Metadata mapped to book schema: {book_data}")
            return book
        except Exception as e:
            logger.error(f"Error mapping metadata to book schema: {e}")
            return None