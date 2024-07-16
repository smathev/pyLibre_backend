from models.book_details.save_details_to_DB import SaveBookDetailsDB
from models.book_details.save_details_check_for_changes_from_db import SaveDetailsCheckForChanges
from models.book_details.new_filenames_if_changes_to_titleORauthor import GenerateNewFilenames
from models.book_details.move_files_based_on_changed_titleORauthor import MoveFilesWhenUpdatingTitleOrAuthor
from models.book_details.save_details_to_epub import SaveDetailsToEpubMetadata
from models.book_details.pack_changes_into_relevant_JSON_objects import PackChangesIntoRelevantJSONObjects

class BookDetailUpdater:
    def __init__(self):
        pass

    def check_for_changes(self, id, data):
        check_for_changes_processor = SaveDetailsCheckForChanges()
        changes_in_data = check_for_changes_processor.check_details_for_changes(id, data)
        return changes_in_data
    
    def pack_changes_into_relevant_JSON_objects(self, changes_in_data):
        change_packager = PackChangesIntoRelevantJSONObjects()
        changes_in_data = change_packager.pack_changes_into_relevant_JSON_objects(changes_in_data)
        return changes_in_data
    
    def save_changes_to_db(self, id, changes_in_data):        
        save_changes_to_db_processor = SaveBookDetailsDB()
        result = save_changes_to_db_processor.save_details_to_db(id, changes_in_data)
        return result
    
    def save_changes_to_epub_metadata(self, id, changes_in_data):
        save_changes_to_epub_metadata_processor = SaveDetailsToEpubMetadata()
        result = save_changes_to_epub_metadata_processor.save_details_to_epub_metadata(id, changes_in_data)
        return result
    
    def move_files_if_changed_titleORauthor(self, id, new_paths):
        move_files_processor = MoveFilesWhenUpdatingTitleOrAuthor()
        new_full_path_epub, new_full_path_cover = move_files_processor.move_files_when_updating_titleORAuthor(id, new_paths)
        return new_full_path_epub, new_full_path_cover

    def set_new_filenames_and_paths_if_changes_in_titleORauthor(self, id, changes_in_data):
        generate_new_filesnames_processor = GenerateNewFilenames()
        new_paths = generate_new_filesnames_processor.new_filenames_when_updating_titleORauthor(id, changes_in_data)
        return new_paths

    def process_changes_update_accordingly(self, id, data):
        changes_in_data = self.check_for_changes(id, data)        
        if 'title' in changes_in_data or 'author' in changes_in_data:
            new_paths = self.set_new_filenames_and_paths_if_changes_in_titleORauthor(id, changes_in_data)
            changes_in_data.update(new_paths)            
            self.save_changes_to_epub_metadata(id, changes_in_data)
            self.move_files_if_changed_titleORauthor(id, new_paths)
        changes_in_data = self.pack_changes_into_relevant_JSON_objects(changes_in_data)
        self.save_changes_to_db(id, changes_in_data)
        status = ({'status': 'success', 'message': 'details have been updated'})
        return status
        
