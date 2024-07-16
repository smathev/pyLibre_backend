# -*- coding: utf-8 -*-

#  This file is part of the Calibre-Web (https://github.com/janeczku/calibre-web)
#    Copyright (C) 2021 OzzieIsaacs
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


#from flask_login import current_user
#from . import ub

from db.db_manager.async_db_manager import AsyncDBManager
from db.classDefinitions.kobo_sync import KoboSync
from db.classDefinitions.archived_books import ArchivedBook
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.book_shelf_links import BookShelfLinks

import datetime
from sqlalchemy.sql.expression import or_, and_, true
from sqlalchemy import exc

class MockUser:
    def __init__(self, id, role_download, kobo_only_shelves_sync):
        self.id = id
        self._role_download = role_download
        self.kobo_only_shelves_sync = kobo_only_shelves_sync

    def role_download(self):
        return self._role_download

def get_mock_user():
    return MockUser(id=1, role_download=True, kobo_only_shelves_sync=False)
db_manager = AsyncDBManager()

async def get_db_session():
    async with db_manager.get_session() as session:
        yield session

# Add the current book id to kobo_synced_books table for current user, if entry is already present,
# do nothing (safety precaution)
async def add_synced_books(book_id):
    current_user = MockUser.get_mock_user()
    async for session in get_db_session():
        is_present = session.query(KoboSync).filter(KoboSync.book_id == book_id)\
            .filter(KoboSync.user_id == current_user.id).count()
        if not is_present:
            synced_book = KoboSync()
            synced_book.user_id = current_user.id
            synced_book.book_id = book_id
            session.add(synced_book)
            await session.commit()


# Select all entries of current book in kobo_synced_books table, which are from current user and delete them
async def remove_synced_book(book_id, all=False, session=None):
    current_user = MockUser.get_mock_user()
    async for session in get_db_session():
        if not all:
            user = KoboSync.user_id == current_user.id
        else:
            user = true()
        if not session:
            session.query(KoboSync).filter(KoboSync.book_id == book_id).filter(user).delete()
            session.commit()
        else:
            session.query(KoboSync).filter(KoboSync.book_id == book_id).filter(user).delete()
            session.commit(_session=session)



async def change_archived_books(book_id, state=None, message=None):
    current_user = MockUser.get_mock_user()
    async for session in get_db_session():
        archived_book = session.query(ArchivedBook).filter(and_(ArchivedBook.user_id == int(current_user.id),
                                                                    ArchivedBook.book_id == book_id)).first()
        if not archived_book:
            archived_book = ArchivedBook(user_id=current_user.id, book_id=book_id)

        archived_book.is_archived = state if state else not archived_book.is_archived
        archived_book.last_modified = datetime.datetime.utcnow()        # toDo. Check utc timestamp

        session.merge(archived_book)
        session.commit(message)
        return archived_book.is_archived


# select all books which are synced by the current user and do not belong to a synced shelf and set them to archive
# select all shelves from current user which are synced and do not belong to the "only sync" shelves
async def update_on_sync_shelfs(user_id):
    current_user = MockUser.get_mock_user()
    async for session in get_db_session():
        books_to_archive = (session.query(KoboSync)
                            .join(BookShelfLinks, KoboSync.book_id == BookShelfLinks.book_id, isouter=True)
                            .join(Shelf, Shelf.user_id == user_id, isouter=True)
                            .filter(or_(Shelf.kobo_sync == 0, Shelf.kobo_sync == None))
                            .filter(KoboSync.user_id == user_id).all())
        for b in books_to_archive:
            change_archived_books(b.book_id, True)
            session.query(KoboSync) \
                .filter(KoboSync.book_id == b.book_id) \
                .filter(KoboSync.user_id == user_id).delete()
            session.commit()

        # Search all shelf which are currently not synced
        shelves_to_archive = session.query(Shelf).filter(Shelf.user_id == user_id).filter(
            Shelf.kobo_sync == 0).all()
        for a in shelves_to_archive:
            #session.add(ShelfArchive(uuid=a.uuid, user_id=user_id))
            session.commit()