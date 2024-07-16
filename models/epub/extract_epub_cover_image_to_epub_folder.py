import os
import shutil
from PIL import Image
from ebooklib import epub
from models.utils_path_manager import path_manager
from loguru import logger

class EpubCoverExtractor:

    static_folder = path_manager.static_folder_full_path
    no_cover_path = os.path.join(static_folder, 'no_cover.jpg')

    def extract_cover(self, metadata):
        directory_path = os.path.dirname(metadata.get('complete_path'))
        file_full_path = os.path.join(directory_path, metadata.get('filename'))
        
        if not os.path.exists(file_full_path):
            logger.warning(f"Epub file not found at {file_full_path}")
            return None

        book = epub.read_epub(file_full_path)
        
        # Extract the book title from the directory path
        book_title = os.path.basename(directory_path)
        cover_image_file = f'{book_title}.jpg'
        output_image_path = os.path.join(directory_path, cover_image_file)

        # Check if the book has a cover
        if book.get_metadata('OPF', 'cover'):
            cover_id = book.get_metadata('OPF', 'cover')[0][1]['content']
            cover_image = book.get_item_with_id(cover_id)
            if cover_image:
                cover_image_path = os.path.join(directory_path, os.path.basename(cover_image.file_name))
                with open(cover_image_path, 'wb') as f:
                    f.write(cover_image.content)

                # Convert the cover image to JPEG
                try:
                    img = Image.open(cover_image_path)
                    img = img.convert('RGB')  # Ensure it's in RGB mode
                    img.save(output_image_path, 'JPEG')
                    os.remove(cover_image_path)  # Remove the original image file
                    logger.info(f"Cover image extracted and converted to JPEG at {output_image_path}")
                except Exception as e:
                    logger.error(f"Failed to convert cover image to JPEG: {e}")
                    shutil.copy(self.no_cover_path, output_image_path)
                    logger.warning(f"Copied default cover image to {output_image_path} due to conversion failure")
            else:
                # Copy no-cover.jpg to output_image_path
                shutil.copy(self.no_cover_path, output_image_path)
                logger.warning(f"No cover image found. Copied default cover image to {output_image_path}")
        else:
            # Copy no-cover.jpg to output_image_path
            shutil.copy(self.no_cover_path, output_image_path)
            logger.warning(f"No cover image found in the ePub file. Copied default cover image to {output_image_path}")

        metadata.update({
            'cover_filename': cover_image_file
        })
        return metadata
