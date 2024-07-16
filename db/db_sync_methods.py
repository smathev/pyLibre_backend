from db.db_manager.sync_db_manager import SyncDBManager
from db.db_manager.async_db_manager import AsyncDBManager
from db.classDefinitions.kobo_sync import KoboSync
from db.classDefinitions.book_shelf_links import BookShelfLinks
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.shelf_archive import ShelfArchive
from db.classDefinitions.archived_books import ArchivedBook
from sqlalchemy.exc import SQLAlchemyError
import datetime
from sqlalchemy.sql.expression import or_, and_, true
from sqlalchemy import exc

from db.classDefinitions.book_shelf_links import BookShelfLinks
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.kobo_sync import KoboSync

from db.db_book_update_book_metadata_by_id import UpdateBookMetadataByID
from loguru import logger

class UpdateBookSyncStatus(SyncDBManager):
    def __init__(self):
        super().__init__()
        self.should_book_sync_checker = CheckBookSyncStatusAgainstShelves()

    def update_book_sync_status(self, book_id):
        should_book_sync_status = self.should_book_sync_checker.check_book_sync_status_against_shelves(book_id)
        try:
            metadata_updater = UpdateBookMetadataByID()
            data_update = {
                'kobo_should_sync': 1 if should_book_sync_status else 0
            }
            update_metadata_result = metadata_updater.update_book_metadata_by_id(book_id, data_update)
            if update_metadata_result:
                logger.info(f'Book sync status updated successfully for book ID {book_id}.')
                return True
            else:
                logger.error(f'Failed to update book sync status for book ID {book_id}.')
                return False
        except Exception as e:
            logger.error(f"Error updating book sync status: {e}")
            return False

class CheckBookSyncStatusAgainstShelves(SyncDBManager):
    def __init__(self):
        super().__init__()

    def check_book_sync_status_against_shelves(self, book_id):
        try:
            with self.Session() as session:
                # Perform a query using a join operation with SQLAlchemy ORM
                result = (self.session.query(BookShelfLinks)
                        .join(Shelf, BookShelfLinks.shelf_id == Shelf.id)
                        .filter(BookShelfLinks.book_id == book_id, Shelf.kobo_should_sync == 1)
                        .count())

                # Check if count is greater than 0
                if result > 0:
                    logger.info(f"Book with ID {book_id} is on at least one syncing shelf.")
                    return True
                else:
                    logger.info(f"Book with ID {book_id} is not on any syncing shelves.")
                    return False
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error checking if book is on syncing shelves: {e}")
            return False

class ShelvesChangeShouldSyncStatus(SyncDBManager):
    def update_shelf_should_sync(self, shelf_id, should_sync):
        try:
            with self.Session() as session:
                # Update kobo_should_sync status for the shelf
                shelf = session.query(Shelf).filter(Shelf.id == shelf_id).first()
                if shelf:
                    shelf.kobo_should_sync = 1 if should_sync else 0
                else:
                    logger.error(f"Shelf with ID {shelf_id} not found.")
                    return

                # Upsert kobo_sync status for books on the shelf
                book_ids = session.query(BookShelfLinks.book_id).filter(BookShelfLinks.shelf_id == shelf_id).all()

                for book_id_tuple in book_ids:
                    book_id = book_id_tuple[0]  # Extract the scalar book_id from the tuple
                    sync_record = session.query(KoboSync).filter(KoboSync.book_id == book_id).first()
                    if sync_record:
                        sync_record.kobo_should_sync = 1 if should_sync else 0
                    else:
                        new_sync_record = KoboSync(
                            book_id=book_id,
                            kobo_should_sync=1 if should_sync else 0
                        )
                        session.add(new_sync_record)

                session.commit()
                logger.info('Synced shelf status changed successfully.')

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error syncing shelf: {e}")



# Add the current book id to kobo_synced_books table for current user, if entry is already present,
# do nothing (safety precaution)
class AddSyncedBook(SyncDBManager):
    def add_synced_books(self, book_id):
        try:
            with self.Session() as session:
                current_user = {}
                current_user.id = 1
                is_present = session.query(KoboSync).filter(KoboSync.book_id == book_id)\
                    .filter(KoboSync.user_id == current_user.id).count()
                if not is_present:
                    synced_book = KoboSync()
                    synced_book.user_id = current_user.id
                    synced_book.book_id = book_id
                    session.add(synced_book)
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding synced book: {e}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding synced book: {e}")


# Select all entries of current book in kobo_synced_books table, which are from current user and delete them
class RemoveSyncedBook(SyncDBManager):
    def remove_synced_book(self, book_id, all=False):
        try:
            with self.Session() as session:
                current_user = {}
                current_user.id = 1
                if not all:
                    user = KoboSync.user_id == current_user.id
                else:
                    user = true()
                if not session:
                    session.query(KoboSync).filter(KoboSync.book_id == book_id).filter(user).delete()
                else:
                    session.query(KoboSync).filter(KoboSync.book_id == book_id).filter(user).delete()
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error removing synced book: {e}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error removing synced book: {e}")


class ChangeArchivedBook(SyncDBManager):
    def change_archived_books(self, book_id, state=None, message=None):
        try:
            with self.Session() as session:
                current_user = {}
                current_user.id = 1
                archived_book = session.query(ArchivedBook).filter(and_(ArchivedBook.user_id == int(current_user.id),
                                                                            ArchivedBook.book_id == book_id)).first()
                if not archived_book:
                    archived_book = ArchivedBook(user_id=current_user.id, book_id=book_id)

                archived_book.is_archived = state if state else not archived_book.is_archived
                archived_book.last_modified = datetime.datetime.utcnow()        # toDo. Check utc timestamp

                session.merge(archived_book)
                return archived_book.is_archived
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error changing archived books: {e}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error changing archived books: {e}")


# select all books which are synced by the current user and do not belong to a synced shelf and set them to archive
# select all shelves from current user which are synced and do not belong to the "only sync" shelves
class UpdateOnSyncShelf(SyncDBManager):
    def update_on_sync_shelfs(self, user_id):
        try:
            with self.Session() as session:

                books_to_archive = (session.query(KoboSync)
                                    .join(BookShelfLinks, KoboSync.book_id == BookShelfLinks.book_id, isouter=True)
                                    .join(Shelf, Shelf.user_id == user_id, isouter=True)
                                    .filter(or_(Shelf.kobo_sync == 0, Shelf.kobo_sync == None))
                                    .filter(KoboSync.user_id == user_id).all())
                for b in books_to_archive:
                    self.change_archived_books(b.book_id, True)
                    session.query(KoboSync) \
                        .filter(KoboSync.book_id == b.book_id) \
                        .filter(KoboSync.user_id == user_id).delete()

                # Search all shelf which are currently not synced
                shelves_to_archive = session.query(Shelf).filter(Shelf.user_id == user_id).filter(
                    Shelf.kobo_sync == 0).all()
                for a in shelves_to_archive:
                    session.add(ShelfArchive(uuid=a.uuid, user_id=user_id))
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating on sync shelves: {e}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating on sync shelves: {e}")