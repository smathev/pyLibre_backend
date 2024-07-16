import os

DIRECTORY_NAMES = {
    'library_folder': 'books',
    'temp_image_folder': '.temp_image_upload',
    'import_folder': 'import',
    'logs_folder': 'logs',
    'static_folder': 'static',
}

FILE_PATHS = {
    'log_file': ('logs_folder', 'log_file.txt'),
    'database_file': ('', 'books.db'),  # Empty string '' means base directory
}

class PathManager:
    def __init__(self):
        self.base_dir = self.find_base_dir()
        self._create_paths()

    @staticmethod
    def find_base_dir():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while not os.path.isfile(os.path.join(current_dir, 'main.py')):
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                raise FileNotFoundError("Could not find 'main.py' in any parent directories from the current script location.")
            current_dir = parent_dir
        return current_dir

    def _create_paths(self):
        for key, directory_name in DIRECTORY_NAMES.items():
            full_path = os.path.join(self.base_dir, directory_name)
            relative_path = os.path.relpath(full_path, start=self.base_dir)

            # Create directory if it doesn't exist
            if not os.path.exists(full_path):
                os.makedirs(full_path)

            setattr(self, f"{key}_full_path", full_path)
            setattr(self, f"{key}_relative_path", relative_path)

        for key, (base_dir, file_name) in FILE_PATHS.items():
            full_path = os.path.join(self.base_dir if not base_dir else getattr(self, f"{base_dir}_full_path"), file_name)
            setattr(self, f"{key}_full_path", full_path)

# Create a global instance
path_manager = PathManager()
