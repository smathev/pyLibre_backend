class PackChangesIntoRelevantJSONObjects:
    def __init__(self):
        pass

    def pack_changes_into_relevant_JSON_objects(self, data):
        changes_in_data = {'book_series_links': {}, 'file_location': {}, 'metadata_changes': {}}

        for key, value in data.items():
            if key == 'series_titles' or key == 'number_in_series':
                changes_in_data['book_series_links'][key] = value
            elif key == 'full_base_path' or key == 'relative_base_path' or key == 'epub_filename' or key == 'cover_filename':
                changes_in_data['file_location'][key] = value
            elif key == 'isbn' or key == 'title' or key == 'author' or key == 'publisher' or key == 'year' or key == 'language' or key == 'genre' or key == 'description' :
                changes_in_data['metadata_changes'][key] = value
        return changes_in_data