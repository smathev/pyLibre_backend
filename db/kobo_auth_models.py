from binascii import hexlify
from datetime import datetime
from os import urandom
from functools import wraps
from db.db_manager.sync_db_manager import SyncDBManager

from loguru import logger

from db.classDefinitions.user import User
from db.classDefinitions.remote_auth_token import RemoteAuthToken
from db.classDefinitions.book import Book

from db.fetch_data_operations import FetchBooksFromDB

#@login_required
class KoboAuthManager(SyncDBManager):
    async def generate_auth_token(self, user_id):
        fetch_books_processor = FetchBooksFromDB()
        
        with self.Session() as session:
            warning = False
            # Generate auth token if none is existing for this user
            auth_token = session.query(RemoteAuthToken).filter(
                RemoteAuthToken.user_id == user_id
            ).filter(RemoteAuthToken.token_type==1).first()

            if not auth_token:
                auth_token = RemoteAuthToken()
                auth_token.user_id = user_id
                auth_token.expiration = datetime.max
                auth_token.auth_token = (hexlify(urandom(16))).decode("utf-8")
                auth_token.token_type = 1

                session.add(auth_token)
                session.commit()

            books = await fetch_books_processor.fetch_books_from_database()

            for book in books:
                kepub_filename = book['kepub_filename']
                if kepub_filename is None:
                    logger.warning(f"Kepub file not found for book: {book['title']}")
                #if 'KEPUB' not in formats and config.config_kepubifypath and 'EPUB' in formats:
                #     helper.convert_book_format(book.id, config.config_calibre_dir, 'EPUB', 'KEPUB', current_user.name)
            return auth_token.auth_token

    def delete_auth_token(self, user_id):
        with self.Session() as session:
            # Invalidate any previously generated Kobo Auth token for this user
            session.query(RemoteAuthToken).filter(RemoteAuthToken.user_id == user_id)\
                .filter(RemoteAuthToken.token_type==1).delete()
            session.commit()
            result = "Token deleted successfully"
            return result

    def get_auth_token(self, user_id):
        with self.Session() as session:
            auth_token = session.query(RemoteAuthToken).filter(
                RemoteAuthToken.user_id == user_id
            ).filter(RemoteAuthToken.token_type==1).first()
            if auth_token:
                return auth_token.auth_token
            else:
                return None