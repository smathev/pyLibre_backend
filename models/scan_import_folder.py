import os
from models.utils_path_manager import path_manager 
from loguru import logger 


class ImportFolderScanner:
    def __init__(self):
        self.import_folder_full_path = path_manager.import_folder_full_path

    def scan_folder(self):
        found_files = []      
        try:
            files_in_import_folder = os.listdir(self.import_folder_full_path)
            for file_name in files_in_import_folder:
                found_files.append(file_name)
            logger.info(f"Scanned folder {self.import_folder_full_path} for files")
            return found_files
        except Exception as e:
            logger.error(f"Error scanning folder {self.import_folder_full_path}: {e}")            
    
    def find_supported_files(self, files):
        supported_extensions = ['.epub', '.mobi', '.azw3']
        supported_files = []
        for file_name in files:
            _, file_extension = os.path.splitext(file_name)
            if file_extension.lower() in supported_extensions:
                supported_files.append(os.path.join(self.import_folder_full_path, file_name))
        return supported_files
    

    def get_relevant_files_in_import_folder(self):
        files_in_import_folder = self.scan_folder()
        supported_files = self.find_supported_files(files_in_import_folder)
        return supported_files

    


