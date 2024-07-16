# base_db_manager.py
from models.utils_path_manager import path_manager

class BaseDBManager:
    def __init__(self):
        self.db_file = path_manager.database_file_full_path

