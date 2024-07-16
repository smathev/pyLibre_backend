import re

class CleanFolderAndFileName:
    def clean_string_for_OS_illegal_characters(self, name):
        # Define a regex pattern for illegal characters
        illegal_chars = r'[<>:"/\\|?*]'
        
        # Replace illegal characters with underscores
        cleaned_name = re.sub(illegal_chars, '_', name)
        
        # Replace spaces with dots
        cleaned_name = cleaned_name.replace(' ', '.')
        
        return cleaned_name