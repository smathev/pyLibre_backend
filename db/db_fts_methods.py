from db.db_manager.sync_db_manager import SyncDBManager
from db.classDefinitions.fts_table import BookFTS

from datetime import datetime
from loguru import logger

class FTSTableManager(SyncDBManager):
    def update_fts_table(self, book):
        try:
            with self.Session() as session:
                # Aggregate authors' names for the book
                authors_names = [aib.author.name for aib in book.book_author_links]
                authors_str = ', '.join(authors_names)
                # Check if the FTS record already exists
                fts_record = session.query(BookFTS).filter_by(rowid=book.id).first()
                if fts_record:
                    # Update existing record
                    fts_record.title = book.title
                    fts_record.authors = authors_str
                else:
                    # Create a new FTS record if it doesn't exist
                    new_fts_record = BookFTS(
                        rowid=book.id,
                        title=book.title,
                        authors=authors_str,
                    )
                    session.add(new_fts_record)
                
                session.commit()
                logger.info('FTS table updated successfully.')
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating FTS table: {e} - {book.id}")
