#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  This file is part of the Calibre-Web (https://github.com/janeczku/calibre-web)
#    Copyright (C) 2018-2019 shavitmichael, OzzieIsaacs
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

import base64
import datetime
import os
import uuid
import zipfile
from time import gmtime, strftime
from urllib.parse import unquote

from fastapi import (FastAPI, 
                     APIRouter, 
                     Request, 
                     HTTPException, 
                     Response, 
                     status, 
                     Depends)
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger
import datetime
import json
import uuid
import os
from sqlalchemy.exc import StatementError
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import and_, or_, not_, func
from sqlalchemy.orm import joinedload
from urllib.parse import unquote
from typing import List, Dict, Any

import models.iso_languages as iso_languages

from db.db_manager.async_db_manager import AsyncDBManager
from db.classDefinitions.kobo_sync import KoboSync
from db.classDefinitions.book import Book
from db.classDefinitions.book_shelf_links import BookShelfLinks
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.file_location import FileLocation
from db.classDefinitions.shelf_archive import ShelfArchive
from db.classDefinitions.kobo_reading_state import KoboReadingState
from db.classDefinitions.archived_books import ArchivedBook
from db.classDefinitions.kobo_bookmark import KoboBookmark
from db.classDefinitions.kobo_reading_state import KoboReadingState
from db.classDefinitions.kobo_statistics import KoboStatistics
from db.classDefinitions.read_book import ReadBook

from db.classDefinitions.publishers import Publisher
from db.classDefinitions.book_publisher_links import BookPublisherLinks

from db.classDefinitions.book_series import BookSeries
from db.classDefinitions.book_series_links import BookSeriesLinks

from db.classDefinitions.author import Author
from db.classDefinitions.book_author_links import BookAuthorLinks

from db.fetch_data_operations import FetchBookDetailsFromDB

from schemas.kobo_schemas import ShelfRequest

from sqlalchemy.exc import SQLAlchemyError

from models.sync_token import SyncToken

import models.kobo_sync_status as kobo_sync_status



import datetime
import httpx
from typing import List, Dict, Any

#from .schemas import SyncToken, BookEntitlement, KoboReadingStateResponse
#from .dependencies import get_current_user, get_db, SyncTokenHeader
#from .helper import create_book_entitlement, get_metadata, get_or_create_reading_state, get_kobo_reading_state_response, sync_shelves, generate_sync_response



import httpx
from fastapi import Request
from starlette.datastructures import Headers

router = APIRouter()

from loguru import logger

from db.kobo_auth_models import KoboAuthManager

from schemas.response_models import BaseResponse, SyncTokenResponse

get_auth_token = KoboAuthManager().get_auth_token
db_manager = AsyncDBManager()

async def get_db_session():
    async with db_manager.get_session() as session:
        yield session


KOBO_FORMATS = {"KEPUB": ["KEPUB"], "EPUB": ["EPUB3", "EPUB"]}
KOBO_STOREAPI_URL = "https://storeapi.kobo.com"
KOBO_IMAGEHOST_URL = "https://cdn.kobo.com/book-images"

COVER_THUMBNAIL_SMALL = 1

SYNC_ITEM_LIMIT = 100

from fastapi import Depends

class MockUser:
    def __init__(self, id, role_download, kobo_only_shelves_sync):
        self.id = id
        self._role_download = role_download
        self.kobo_only_shelves_sync = kobo_only_shelves_sync

    def role_download(self):
        return self._role_download

def get_mock_user():
    return MockUser(id=1, role_download=True, kobo_only_shelves_sync=False)


current_user = get_mock_user()

CONNECTION_SPECIFIC_HEADERS = [
    "connection",
    "content-encoding",
    "content-length",
    "transfer-encoding",
]
def get_store_url_for_current_request(request: Request):
    __, __, request_path_with_auth_token = request.url.path.rpartition("/kobo/")
    __, __, request_path = request_path_with_auth_token.rstrip("?").partition("/")
    return KOBO_STOREAPI_URL + "/" + request_path

def convert_to_kobo_timestamp_string(date_added):
    try:
        return date_added.strftime("%Y-%m-%dT%H:%M:%SZ")
    except AttributeError as exc:
        logger.debug("Timestamp not valid: {}".format(exc))
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
# TODO implement the true config_db to get these values. Set to true at the moment - kobo_sync
def get_kobo_activated():
    return True
    config.config_kobo_sync


async def make_request_to_kobo_store(request: Request, sync_token=None):
    try:
        # Log the raw headers for debugging
        raw_headers = request.headers.raw
        logger.info(f"Raw headers: {raw_headers}")
        
        # Directly convert raw headers to a dictionary
        outgoing_headers = {key.decode(): value.decode() for key, value in raw_headers}
        logger.info(f"Outgoing headers: {outgoing_headers}")
        
        # Remove 'host' header if present
        outgoing_headers.pop("host", None)
        
        # Set sync token header if available
        if sync_token:
            sync_token.set_kobo_store_header(outgoing_headers)
        
        # Make the request to the Kobo store
        async with httpx.AsyncClient(verify=False) as client:
            store_response = await client.request(
                method=request.method,
                url=get_store_url_for_current_request(request),
                headers=outgoing_headers,
                data=await request.body(),
                follow_redirects=False,
                timeout=(2, 10)
            )
        
        logger.debug("Content: " + store_response.text)
        logger.debug("StatusCode: " + str(store_response.status_code))
        return store_response
    except Exception as e:
        logger.error(f"Error in make_request_to_kobo_store: {e}")
        raise

async def redirect_or_proxy_request(request: Request, sync_token=None):
    if get_kobo_activated:
        #config.config_kobo_proxy:
        if request.method == "GET":
            return RedirectResponse(url=get_store_url_for_current_request(request), status_code=307)
        else:
            store_response = await make_request_to_kobo_store(request, sync_token)
            
            response_headers = store_response.headers
            for header_key in CONNECTION_SPECIFIC_HEADERS:
                response_headers.pop(header_key, None)

            return Response(
                content=store_response.content,
                status_code=store_response.status_code,
                headers=dict(response_headers)
            )
    else:
        return JSONResponse(content={})

@router.get("/v1/library/sync", tags=["Kobo"])
async def handle_sync_request(
    request: Request,
    current_user: MockUser = Depends(get_mock_user),
    session: AsyncSession = Depends(get_db_session),  # Use the session dependency
):
    if not current_user.role_download():
        logger.info("Users need download permissions for syncing library to Kobo reader")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    sync_token = SyncToken.from_headers(request.headers)
    logger.info("Kobo library sync request received")
    logger.info(f"SyncToken: {sync_token}")

    query = select(func.count()).select_from(KoboSync).where(KoboSync.user_id == current_user.id)
    result = await session.execute(query)
    count = result.scalar()

    if not count:
        sync_token.books_date_updated = datetime.datetime.min
        sync_token.books_last_created = datetime.datetime.min
        sync_token.reading_state_date_updated = datetime.datetime.min

        new_books_date_updated = sync_token.books_date_updated  # needed for sync selected shelves only
        new_books_last_created = sync_token.books_last_created  # needed to distinguish between new and changed entitlement
        new_reading_state_date_updated = sync_token.reading_state_date_updated
        new_archived_date_updated = datetime.datetime.min
        sync_results = []

        only_kobo_shelves = current_user.kobo_only_shelves_sync
        base_query = (
            select(Book, ArchivedBook.date_updated, ArchivedBook.is_archived)
            .join(FileLocation)
            .outerjoin(
                ArchivedBook,
                and_(
                    Book.id == ArchivedBook.book_id,
                    ArchivedBook.user_id == current_user.id
                )
            )
            .filter(
                Book.id.notin_(
                    select(KoboSync.book_id)
                    .filter(KoboSync.user_id == current_user.id)
                )
            )
            .options(joinedload(Book.book_author_links).joinedload(BookAuthorLinks.author))  # Eagerly load authors
            .options(joinedload(Book.book_publisher_links).joinedload(BookPublisherLinks.publisher))  # Eagerly load publishers
            .options(joinedload(Book.book_series_links).joinedload(BookSeriesLinks.book_series))  # Eagerly load series
        )

        if only_kobo_shelves:
            base_query = (
                base_query
                .add_columns(BookShelfLinks.date_added)
                .filter(
                    BookShelfLinks.date_added > sync_token.books_date_updated
                )
                .filter(
                    not_(
                        or_(
                            FileLocation.kepub_filename.is_(None),
                            FileLocation.kepub_filename == ''
                        )
                    )
                )
                .join(BookShelfLinks, Book.id == BookShelfLinks.book_id)
                .join(Shelf)
                .filter(
                    Shelf.user_id == current_user.id
                )
                .filter(
                    Shelf.kobo_should_sync
                )
                .order_by(Book.id)
                .order_by(ArchivedBook.date_updated)
                .distinct()
            )
        else:
            base_query = (
                base_query
                .filter(
                    or_(
                        FileLocation.kepub_filename.is_(None),
                        FileLocation.kepub_filename == ''
                    )
                )
                .order_by(Book.date_updated)
                .order_by(Book.id)
            )

        changed_entries_query = base_query
        reading_states_in_new_entitlements = []
        result = await session.execute(changed_entries_query)
        books = result.unique().all()

        for book in books:
            kobo_reading_state = await get_or_create_reading_state(book.Book.id, current_user)
            entitlement = {
                "BookEntitlement": create_book_entitlement(book.Book, archived=(book.is_archived == True)),
                "BookMetadata": get_metadata(book.Book),
            }

            if kobo_reading_state.date_updated > sync_token.reading_state_date_updated:
                entitlement["ReadingState"] = get_kobo_reading_state_response(book.Book, kobo_reading_state)
                new_reading_state_date_updated = max(new_reading_state_date_updated, kobo_reading_state.date_updated)
                reading_states_in_new_entitlements.append(book.Book.id)

            ts_created = book.Book.date_added.replace(tzinfo=None)
            try:
                ts_created = max(ts_created, book.date_added)
            except AttributeError:
                pass

            if ts_created > sync_token.books_last_created:
                sync_results.append({"NewEntitlement": entitlement})
            else:
                sync_results.append({"ChangedEntitlement": entitlement})

            new_books_date_updated = max(book.Book.date_updated.replace(tzinfo=None), new_books_date_updated)
            try:
                new_books_date_updated = max(new_books_date_updated, book.date_added)
            except AttributeError:
                pass

            new_books_last_created = max(ts_created, new_books_last_created)
            kobo_sync_status.add_synced_books(book.Book.id)

        max_change_query = select(ArchivedBook).filter(ArchivedBook.is_archived).filter(ArchivedBook.user_id == current_user.id).order_by(
            func.datetime(ArchivedBook.date_updated).desc()).limit(1)
        max_change = await session.execute(max_change_query)
        max_change = max_change.scalar()
        max_change = max_change.date_updated if max_change else new_archived_date_updated
        new_archived_date_updated = max(new_archived_date_updated, max_change)

        book_count_query = select(func.count()).select_from(changed_entries_query.subquery())
        book_count_result = await session.execute(book_count_query)
        book_count = book_count_result.scalar()
        cont_sync = bool(book_count)
        logger.debug(f"Remaining books to Sync: {book_count}")

        changed_reading_states_query = select(KoboReadingState)
        if only_kobo_shelves:
            changed_reading_states_query = changed_reading_states_query.join(BookShelfLinks, KoboReadingState.book_id == BookShelfLinks.book_id).join(Shelf).filter(
                current_user.id == Shelf.user_id).filter(Shelf.kobo_should_sync, or_(
                KoboReadingState.date_updated > sync_token.reading_state_date_updated, func.datetime(
                    BookShelfLinks.date_added) > sync_token.books_date_updated)).distinct()
        else:
            changed_reading_states_query = changed_reading_states_query.filter(KoboReadingState.date_updated > sync_token.reading_state_date_updated)

        changed_reading_states_query = changed_reading_states_query.filter(
            and_(KoboReadingState.user_id == current_user.id, KoboReadingState.book_id.notin_(reading_states_in_new_entitlements))).order_by(
            KoboReadingState.date_updated)

        count_result = await session.execute(select(func.count()).select_from(changed_reading_states_query.subquery()))
        cont_sync |= bool(count_result.scalar() > SYNC_ITEM_LIMIT)
        
        changed_reading_states = await session.execute(changed_reading_states_query.limit(SYNC_ITEM_LIMIT))
        for kobo_reading_state in changed_reading_states.scalars().all():
            book = await session.execute(select(Book).filter(Book.id == kobo_reading_state.book_id)).scalar_one_or_none()
            if book:
                sync_results.append({
                    "ChangedReadingState": {
                        "ReadingState": get_kobo_reading_state_response(book, kobo_reading_state)
                    }
                })
                new_reading_state_date_updated = max(new_reading_state_date_updated, kobo_reading_state.date_updated)

        sync_shelves(sync_token, sync_results, only_kobo_shelves)

        if not cont_sync:
            sync_token.books_last_created = new_books_last_created
        sync_token.books_date_updated = new_books_date_updated
        sync_token.archive_date_updated = new_archived_date_updated
        sync_token.reading_state_date_updated = new_reading_state_date_updated

        return await generate_sync_response(sync_token, sync_results, cont_sync)

async def generate_sync_response(sync_token, sync_results, set_cont=False):
    extra_headers = {}
    if get_kobo_activated() and not set_cont:
        # Merge in sync results from the official Kobo store.
        try:
            store_response = await make_request_to_kobo_store(sync_token)

            store_sync_results = store_response.json()
            sync_results += store_sync_results
            sync_token.merge_from_store_response(store_response)
            extra_headers["x-kobo-sync"] = store_response.headers.get("x-kobo-sync")
            extra_headers["x-kobo-sync-mode"] = store_response.headers.get("x-kobo-sync-mode")
            extra_headers["x-kobo-recent-reads"] = store_response.headers.get("x-kobo-recent-reads")

        except Exception as ex:
            logger.error("Failed to receive or parse response from Kobo's sync endpoint: {}".format(ex))
    
    if set_cont:
        extra_headers["x-kobo-sync"] = "continue"
    
    sync_token.to_headers(extra_headers)

    response = JSONResponse(content=sync_results, headers=extra_headers)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@router.get("/v1/library/{book_uuid}/metadata", tags=["Kobo"])
async def handle_metadata_request(book_uuid: str, request: Request, db: AsyncSession = Depends(get_db_session)):
    logger.info(f"Kobo library metadata request received for book {book_uuid}")
    async with db as session:
        result = await session.execute(select(Book).filter(Book.uuid == book_uuid))
        book = result.scalars().one_or_none()
        if not book or not book.data:
            logger.info(f"Book {book_uuid} not found in database")
            return await redirect_or_proxy_request(request)

        metadata = get_metadata(book)
        response = JSONResponse(content=[metadata], ensure_ascii=False)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

@router.post("/v1/library/tags", status_code=status.HTTP_201_CREATED, tags=["Kobo"])
async def handle_tag_create(request_body: ShelfRequest, db: AsyncSession = Depends(get_db_session)):
    try:
        name = request_body.Name
        items = request_body.Items
        if not name:
            raise TypeError
    except (KeyError, TypeError):
        logger.debug("Received malformed v1/library/tags request.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed tags POST request. Data has empty 'Name', missing 'Name' or 'Items' field")

    async with db_manager.get_session() as session:

        query = select(Shelf).filter(Shelf.shelf_name == name, Shelf.user_id == current_user.id).options(joinedload(Shelf.book_shelf_links).joinedload(BookShelfLinks.book))
        result = await session.execute(query)
        shelves = result.unique().scalars().all()
        if len(shelves) == 1:
            shelf = shelves[0]
        elif len(shelves) == 0:
            shelf = None
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Multiple shelves found")
        if shelf and not check_shelf_edit_permissions(shelf):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unauthorized to create shelf.")

        if not shelf:
            shelf = Shelf(user_id=current_user.id, shelf_name=name, uuid=str(uuid.uuid4()))
            session.add(shelf)

        #items_unknown_to_calibre = add_items_to_shelf(items, shelf, session)
        items_unknown_to_calibre = add_items_to_shelf(items, shelf)
        if items_unknown_to_calibre:
            logger.debug("Received request to add unknown books to a collection. Silently ignoring items.")
        await session.commit()
        return JSONResponse(content=str(shelf.uuid))

# @router.put("/v1/library/tags/{tag_id}", status_code=status.HTTP_200_OK, tags=["Kobo"])
# async def handle_tag_update(tag_id: str, request: Request, current_user=1, db: AsyncSession = Depends(get_db_session)):
#     async with db as session:
#         shelf = await session.query(Shelf).filter(Shelf.uuid == tag_id, Shelf.user_id == current_user.id).one_or_none()
#         if not shelf:
#             logger.debug("Received Kobo tag update request on a collection unknown to CalibreWeb")
#             if get_kobo_activated():
#                 return await redirect_or_proxy_request(request)
#             else:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection isn't known to CalibreWeb")
#
#         if request.method == "DELETE":
#             if not delete_shelf_helper(shelf, session):
#                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error deleting Shelf")
#         else:
#             try:
#                 shelf_request = await request.json()
#                 name = shelf_request["Name"]
#                 shelf.name = name
#                 session.merge(shelf)
#                 await session.commit()
#             except (KeyError, TypeError):
#                 logger.debug("Received malformed v1/library/tags rename request.")
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed tags POST request. Data is missing 'Name' field")
#         return JSONResponse(content=' ', status_code=status.HTTP_200_OK)

@router.put("/v1/library/tags/{tag_id}", status_code=status.HTTP_200_OK, tags=["Kobo"])
async def handle_tag_update(tag_id: str, request: Request, current_user=1, db: AsyncDBManager = Depends(AsyncDBManager)):
    async with db() as session:
        shelf = await session.query(Shelf).filter(Shelf.uuid == tag_id, Shelf.user_id == current_user.id).one_or_none()
        if not shelf:
            logger.debug("Received Kobo tag update request on a collection unknown to CalibreWeb")
            if get_kobo_activated():
                return await redirect_or_proxy_request(request)
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection isn't known to CalibreWeb")

        if request.method == "DELETE":
            #if not shelf_lib.delete_shelf_helper(shelf, session):
            if not delete_shelf_helper(shelf, session):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error deleting Shelf")
        else:
            try:
                shelf_request = await request.json()
                name = shelf_request["Name"]
                shelf.name = name
                session.merge(shelf)
                await session.commit()
            except (KeyError, TypeError):
                logger.debug("Received malformed v1/library/tags rename request.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed tags POST request. Data is missing 'Name' field")
        return JSONResponse(content=' ', status_code=status.HTTP_200_OK)

@router.post("/v1/library/tags/{tag_id}/items", status_code=status.HTTP_201_CREATED, tags=["Kobo"])
async def handle_tag_add_item(tag_id: str, request: Request, current_user=1, db: AsyncDBManager = Depends(AsyncDBManager)):
    try:
        tag_request = await request.json()
        items = tag_request["Items"]
    except (KeyError, TypeError):
        logger.debug("Received malformed v1/library/tags/{tag_id}/items request.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed tags POST request. Data is missing 'Items' field")

    async with db() as session:
        shelf = await session.query(Shelf).filter(Shelf.uuid == tag_id, Shelf.user_id == current_user.id).one_or_none()
        if not shelf:
            logger.debug("Received Kobo request on a collection unknown to CalibreWeb")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection isn't known to CalibreWeb")

        if not check_shelf_edit_permissions(shelf):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unauthorized to edit shelf.")

        items_unknown_to_calibre = add_items_to_shelf(items, shelf, session)
        if items_unknown_to_calibre:
            logger.debug("Received request to add an unknown book to a collection. Silently ignoring item.")

        session.merge(shelf)
        await session.commit()
        return JSONResponse(content='', status_code=status.HTTP_201_CREATED)

@router.post("/v1/library/tags/{tag_id}/items/delete", status_code=status.HTTP_200_OK, tags=["Kobo"])
async def handle_tag_remove_item(tag_id: str, request: Request, current_user=1, db: AsyncDBManager = Depends(AsyncDBManager)):
    try:
        tag_request = await request.json()
        items = tag_request["Items"]
    except (KeyError, TypeError):
        logger.debug("Received malformed v1/library/tags/{tag_id}/items/delete request.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed tags POST request. Data is missing 'Items' field")

    async with db() as session:
        shelf = await session.query(Shelf).filter(Shelf.uuid == tag_id, Shelf.user_id == current_user.id).one_or_none()
        if not shelf:
            logger.debug("Received a request to remove an item from a Collection unknown to CalibreWeb.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection isn't known to CalibreWeb")

        #if not shelf_lib.check_shelf_edit_permissions(shelf):
        #    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unauthorized to edit shelf.")

        items_unknown_to_calibre = []
        for item in items:
            try:
                if item["Type"] != "ProductRevisionTagItem":
                    items_unknown_to_calibre.append(item)
                    continue

                book = await session.query(Book).filter(Book.uuid == item["RevisionId"]).one_or_none()
                if not book:
                    items_unknown_to_calibre.append(item)
                    continue

                await session.query(BookShelfLinks).filter(BookShelfLinks.book_id == book.id).delete()
            except KeyError:
                items_unknown_to_calibre.append(item)

        await session.commit()

        if items_unknown_to_calibre:
            logger.debug("Received request to remove an unknown book from a collection. Silently ignoring item.")

        return JSONResponse(content='', status_code=status.HTTP_200_OK)

def get_metadata(book):
    download_urls = []
    #kepub = [data for data in book.data if data.format == 'KEPUB']

    # for book_data in kepub if len(kepub) > 0 else book.data:
    #     if book_data.format not in KOBO_FORMATS:
    #         continue
    #     for kobo_format in KOBO_FORMATS[book_data.format]:
    #         pass
            # # log.debug('Id: %s, Format: %s' % (book.id, kobo_format))
            # try:
            #     if get_epub_layout(book, book_data) == 'pre-paginated':
            #         kobo_format = 'EPUB3FL'
            #     download_urls.append(
            #         {
            #             "Format": kobo_format,
            #             "Size": book_data.uncompressed_size,
            #             "Url": get_download_url_for_book(book.id, book_data.format),
            #             # The Kobo forma accepts platforms: (Generic, Android)
            #             "Platform": "Generic",
            #             # "DrmType": "None", # Not required
            #         }
            #     )
            # except (zipfile.BadZipfile, FileNotFoundError) as e:
            #     log.error(e)

    book_uuid = book.uuid
    metadata = {
        "Categories": ["00000000-0000-0000-0000-000000000001", ],
        #"Contributors": get_author(authors),
        "CoverImageId": book_uuid,
        "CrossRevisionId": book_uuid,
        "CurrentDisplayPrice": {"CurrencyCode": "USD", "TotalAmount": 0},
        "CurrentLoveDisplayPrice": {"TotalAmount": 0},
        "Description": get_description(book),
        "DownloadUrls": download_urls,
        "EntitlementId": book_uuid,
        "ExternalIds": [],
        "Genre": "00000000-0000-0000-0000-000000000001",
        "IsEligibleForKoboLove": False,
        "IsInternetArchive": False,
        "IsPreOrder": False,
        "IsSocialEnabled": True,
        "Language": get_language(book),
        "Language": book.language,
        "PhoneticPronunciations": {},
        "PublicationDate": convert_to_kobo_timestamp_string(book.publication_date),
        "Publisher": {"Imprint": "", "Name": get_publisher(book), },
        #"Publisher": {"Imprint": "", "Name": publisher, },
        "RevisionId": book_uuid,
        "Title": book.title,
        "WorkId": book_uuid,
    }
    metadata.update(get_author(book))

    if get_series(book):
        name = get_series(book)
        metadata["Series"] = {
            "Name": get_series(book),
            "Number": get_seriesindex(book),        # ToDo Check int() ?
            "NumberFloat": float(get_seriesindex(book)),
            # Get a deterministic id based on the series name.
            "Id": str(uuid.uuid3(uuid.NAMESPACE_DNS, name)),
        }

    return metadata
def current_time():
    return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())


def get_description(book):
    if not book.description:
        return None
    return book.description
    # if not book.comments:
    #     return None
    # return book.comments[0].text


def get_author(book):
    if not book.book_author_links:
        return {"Contributors": None}
    author_list = []
    autor_roles = []
    for author in book.book_author_links:
        autor_roles.append({"Name": author.author.name})
        author_list.append(author.author.name)
    return {"ContributorRoles": autor_roles, "Contributors": author_list}


def get_publisher(book):
    if not book.book_publisher_links:
        return None
    return book.book_publisher_links[0].publisher.name


def get_series(book):
    if not book.book_series_links:
        return None
    #TODO Have to fix this part also!
    return None
    #return book.series[0].name


def get_seriesindex(book):
    return book.series_index or 1


def get_language(book):
    if not book.language:
        return 'en'
    if book.language:
        return 'en'
    # TODO - fix this, if needed - it will always return that the book is in english.
    if book.language == 'UND':
        return 'en'
    if book.language == 'ar-SA':
        return 'en'
    return iso_languages.get(book.language).part1

async def sync_shelves(sync_token, sync_results, only_kobo_shelves=False, db: AsyncDBManager = Depends(AsyncDBManager)):
    new_tags_date_updated = sync_token.tags_date_updated

    async with db() as session:
        for shelf in await session.query(ShelfArchive).filter(ShelfArchive.user_id == current_user.id).all():
            new_tags_date_updated = max(shelf.date_updated, new_tags_date_updated)
            sync_results.append({
                "DeletedTag": {
                    "Tag": {
                        "Id": shelf.uuid,
                        "LastModified": convert_to_kobo_timestamp_string(shelf.date_updated)
                    }
                }
            })
            await session.delete(shelf)
            await session.commit()

        extra_filters = []
        if only_kobo_shelves:
            for shelf in await session.query(Shelf).filter(
                func.datetime(Shelf.date_updated) > sync_token.tags_date_updated,
                Shelf.user_id == current_user.id,
                not Shelf.kobo_should_sync
            ).all():
                sync_results.append({
                    "DeletedTag": {
                        "Tag": {
                            "Id": shelf.uuid,
                            "LastModified": convert_to_kobo_timestamp_string(shelf.date_updated)
                        }
                    }
                })
            extra_filters.append(Shelf.kobo_should_sync)

        shelflist = await session.query(Shelf).outerjoin(BookShelfLinks).filter(
            or_(func.datetime(Shelf.date_updated) > sync_token.tags_date_updated,
                func.datetime(BookShelfLinks.date_added) > sync_token.tags_date_updated),
            Shelf.user_id == current_user.id,
            *extra_filters
        ).distinct().order_by(func.datetime(Shelf.date_updated).asc()).all()

        for shelf in shelflist:
            #if not shelf_lib.check_shelf_view_permissions(shelf):
            if not check_shelf_view_permissions(shelf):
                continue

            new_tags_date_updated = max(shelf.date_updated, new_tags_date_updated)
            tag = create_kobo_tag(shelf)
            if not tag:
                continue

            if shelf.created > sync_token.tags_date_updated:
                sync_results.append({
                    "NewTag": tag
                })
            else:
                sync_results.append({
                    "ChangedTag": tag
                })
        sync_token.tags_date_updated = new_tags_date_updated
        await session.commit()

def create_kobo_tag(shelf):
    tag = {
        "Created": convert_to_kobo_timestamp_string(shelf.created),
        "Id": shelf.uuid,
        "Items": [],
        "LastModified": convert_to_kobo_timestamp_string(shelf.date_updated),
        "Name": shelf.name,
        "Type": "UserTag"
    }
    for book_shelf in shelf.books:
        book_fetcher = FetchBookDetailsFromDB()
        book = book_fetcher.fetch_book_details_by_id(book_shelf.book_id)
        #book = calibre_db.get_book(book_shelf.book_id)
        if not book:
            logger.info("Book (id: %s) in BookShelf (id: %s) not found in book database", book_shelf.book_id, shelf.id)
            continue
        tag["Items"].append(
            {
                "RevisionId": book.uuid,
                "Type": "ProductRevisionTagItem"
            }
        )
    return {"Tag": tag}

@router.put("/v1/library/{book_uuid}/state", tags=["Kobo"])
async def handle_state_request(book_uuid: str, request: Request, db: AsyncDBManager = Depends(get_db_session)):
    async with db as session:
        result = await session.execute(select(Book).filter(Book.uuid == book_uuid))
        book = result.scalars().one_or_none()
        if not book or not book.title:
            logger.info(f"Book {book_uuid} not found in database")
            return await redirect_or_proxy_request(request)

        kobo_reading_state = await get_or_create_reading_state(book.id)

        if request.method == "GET":
            return JSONResponse(content=[get_kobo_reading_state_response(book, kobo_reading_state)])
        else:
            update_results_response = {"EntitlementId": book_uuid}

            try:
                request_data = await request.json()
                request_reading_state = request_data["ReadingStates"][0]

                request_bookmark = request_reading_state["CurrentBookmark"]
                if request_bookmark:
                    current_bookmark = kobo_reading_state.current_bookmark
                    current_bookmark.progress_percent = request_bookmark["ProgressPercent"]
                    current_bookmark.content_source_progress_percent = request_bookmark["ContentSourceProgressPercent"]
                    location = request_bookmark["Location"]
                    if location:
                        current_bookmark.location_value = location["Value"]
                        current_bookmark.location_type = location["Type"]
                        current_bookmark.location_source = location["Source"]
                    update_results_response["CurrentBookmarkResult"] = {"Result": "Success"}

                request_statistics = request_reading_state["Statistics"]
                if request_statistics:
                    statistics = kobo_reading_state.statistics
                    statistics.spent_reading_minutes = int(request_statistics["SpentReadingMinutes"])
                    statistics.remaining_time_minutes = int(request_statistics["RemainingTimeMinutes"])
                    update_results_response["StatisticsResult"] = {"Result": "Success"}

                request_status_info = request_reading_state["StatusInfo"]
                if request_status_info:
                    book_read = kobo_reading_state.book_read_link
                    new_book_read_status = get_ub_read_status(request_status_info["Status"])
                    if new_book_read_status == ReadBook.STATUS_IN_PROGRESS and new_book_read_status != book_read.read_status:
                        book_read.times_started_reading += 1
                        book_read.last_time_started_reading = datetime.datetime.utcnow()
                    book_read.read_status = new_book_read_status
                    update_results_response["StatusInfoResult"] = {"Result": "Success"}

            except (KeyError, TypeError, ValueError, StatementError):
                logger.debug("Received malformed v1/library/{book_uuid}/state request.")
                await session.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed request data is missing 'ReadingStates' key")

            session.merge(kobo_reading_state)
            await session.commit()
            return JSONResponse(content={"RequestResult": "Success", "UpdateResults": [update_results_response]})

@router.get("/{book_uuid}/{width}/{height}/{isGreyscale}/image.jpg", tags=["Kobo"])
@router.get("/{book_uuid}/{width}/{height}/{Quality}/{isGreyscale}/image.jpg", tags=["Kobo"])
async def handle_cover_image_request(request: Request, book_uuid: str, width: int, height: int, Quality: str = "", isGreyscale: str = "false"):
    try:
        resolution = None if int(height) > 1000 else COVER_THUMBNAIL_SMALL
    except ValueError:
        logger.error(f"Requested height {height} of book {book_uuid} is invalid")
        resolution = COVER_THUMBNAIL_SMALL
    book_cover = get_book_cover_with_uuid(book_uuid, resolution=resolution)
    if book_cover:
        logger.debug(f"Serving local cover image of book {book_uuid}")
        return book_cover

    if not get_kobo_activated():
        logger.debug(f"Returning 404 for cover image of unknown book {book_uuid}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Book not found"})

    logger.debug(f"Redirecting request for cover image of unknown book {book_uuid} to Kobo")
    return RedirectResponse(url=KOBO_IMAGEHOST_URL + f"/{book_uuid}/{width}/{height}/false/image.jpg", status_code=307)

@router.get("/")
async def top_level_endpoint():
    return JSONResponse(content={})

@router.delete("/v1/library/{book_uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["Kobo"])
async def handle_book_deletion_request(book_uuid: str, request: Request, db: AsyncDBManager = Depends(AsyncDBManager)):
    logger.info(f"Kobo book delete request received for book {book_uuid}")
    async with db() as session:
        book = await session.query(Book).filter(Book.uuid == book_uuid).one_or_none()
        if not book:
            logger.info(f"Book {book_uuid} not found in database")
            return await redirect_or_proxy_request(request)

        book_id = book.id
        is_archived = kobo_sync_status.change_archived_books(book_id, True)
        if is_archived:
            kobo_sync_status.remove_synced_book(book_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/v1/auth/device", tags=["Kobo"])
async def handle_auth_request(request: Request):
    logger.debug('Kobo Auth request')
    if get_kobo_activated():
        try:
            return await redirect_or_proxy_request(request)
        except Exception:
            logger.error("Failed to receive or parse response from Kobo's auth endpoint. Falling back to un-proxied mode.")
    return make_calibre_web_auth_response(request)

@router.get("/v1/initialization", tags=["Kobo"])
async def handle_init_request(request: Request):
    logger.info('Init')

    kobo_resources = None
    if get_kobo_activated():
        try:
            logger.info(f"Incoming headers: {request.headers.raw}")
            store_response = await make_request_to_kobo_store(request)
            store_response_json = store_response.json()
            if "Resources" in store_response_json:
                kobo_resources = store_response_json["Resources"]
        except Exception:
            logger.error("Failed to receive or parse response from Kobo's init endpoint. Falling back to un-proxied mode.")
    if not kobo_resources:
        kobo_resources = NATIVE_KOBO_RESOURCES()

    if not request.app.state.is_proxied:
        logger.debug('Kobo: Received unproxied request, changed request port to external server port')
        if ':' in request.headers.get('host') and not request.headers.get('host').endswith(']'):
            host = "".join(request.headers.get('host').split(':')[:-1])
        else:
            host = request.headers.get('host')
        # TODO - define a proper way to get the default config_external_port - like in the original code:
        pyLib_backend_url = f"{request.url.scheme}://{host}:{8000}"
        #calibre_web_url = f"{request.url.scheme}://{host}:{config.config_external_port}"
        logger.debug(f'Kobo: Received unproxied request, changed request url to {pyLib_backend_url}')
        kobo_resources["image_host"] = pyLib_backend_url
        kobo_resources["image_url_quality_template"] = unquote(pyLib_backend_url + request.url_for("handle_cover_image_request", book_uuid="{ImageId}", width="{width}", height="{height}", Quality='{Quality}', isGreyscale='isGreyscale'))
        kobo_resources["image_url_template"] = unquote(pyLib_backend_url + request.url_for("handle_cover_image_request", book_uuid="{ImageId}", width="{width}", height="{height}", isGreyscale='false'))
    else:
        kobo_resources["image_host"] = request.url_for("web.index", _external=True).strip("/")
        kobo_resources["image_url_quality_template"] = unquote(request.url_for("handle_cover_image_request", book_uuid="{ImageId}", width="{width}", height="{height}", Quality='{Quality}', isGreyscale='isGreyscale', _external=True))
        kobo_resources["image_url_template"] = unquote(request.url_for("handle_cover_image_request", book_uuid="{ImageId}", width="{width}", height="{height}", isGreyscale='false', _external=True))

    response = JSONResponse(content={"Resources": kobo_resources})
    response.headers["x-kobo-apitoken"] = "e30="
    return response
#@router.get("/download/{book_id}/{book_format}")
#async def download_book(book_id: str, book_format: str):
#    return get_download_link(book_id, book_format, "kobo")

def get_ub_read_status(kobo_read_status):
    string_to_enum_map = {
        None: None,
        "ReadyToRead": ReadBook.STATUS_UNREAD,
        "Finished": ReadBook.STATUS_FINISHED,
        "Reading": ReadBook.STATUS_IN_PROGRESS,
    }
    return string_to_enum_map[kobo_read_status]

def create_book_entitlement(book, archived):
    book_uuid = str(book.uuid)
    return {
        "Accessibility": "Full",
        "ActivePeriod": {"From": convert_to_kobo_timestamp_string(datetime.datetime.utcnow())},
        "Created": convert_to_kobo_timestamp_string(book.date_added),
        "CrossRevisionId": book_uuid,
        "Id": book_uuid,
        "IsRemoved": archived,
        "IsHiddenFromArchive": False,
        "IsLocked": False,
        "LastModified": convert_to_kobo_timestamp_string(book.date_updated),
        "OriginCategory": "Imported",
        "RevisionId": book_uuid,
        "Status": "Active",
    }

async def get_or_create_reading_state(book_id: int):
    async with db_manager.get_session() as session:
        query = (
            select(ReadBook)
            .filter(and_(ReadBook.book_id == book_id, ReadBook.user_id == int(current_user.id)))
            .options(joinedload(ReadBook.kobo_reading_state).joinedload(KoboReadingState.current_bookmark))
            .options(joinedload(ReadBook.kobo_reading_state).joinedload(KoboReadingState.statistics))
        )
        result = await session.execute(query)
        book_read = result.scalar_one_or_none()

        if not book_read:
            book_read = ReadBook(user_id=current_user.id, book_id=book_id)
            session.add(book_read)

        if not book_read.kobo_reading_state:
            kobo_reading_state = KoboReadingState(user_id=book_read.user_id, book_id=book_id)
            kobo_reading_state.current_bookmark = KoboBookmark()
            kobo_reading_state.statistics = KoboStatistics()
            book_read.kobo_reading_state = kobo_reading_state
            session.add(kobo_reading_state)

        await session.commit()
        return book_read.kobo_reading_state

def get_kobo_reading_state_response(book, kobo_reading_state):
    return {
        "EntitlementId": book.uuid,
        "Created": convert_to_kobo_timestamp_string(book.date_added),
        "LastModified": convert_to_kobo_timestamp_string(kobo_reading_state.date_updated),
        # AFAICT PriorityTimestamp is always equal to LastModified.
        "PriorityTimestamp": convert_to_kobo_timestamp_string(kobo_reading_state.priority_timestamp),
        "StatusInfo": get_status_info_response(kobo_reading_state.book_read_link),
        "Statistics": get_statistics_response(kobo_reading_state.statistics),
        "CurrentBookmark": get_current_bookmark_response(kobo_reading_state.current_bookmark),
    }

def get_status_info_response(book_read):
    resp = {
        "LastModified": convert_to_kobo_timestamp_string(book_read.date_updated),
        "Status": get_read_status_for_kobo(book_read),
        "TimesStartedReading": book_read.times_started_reading,
    }
    if book_read.last_time_started_reading:
        resp["LastTimeStartedReading"] = convert_to_kobo_timestamp_string(book_read.last_time_started_reading)
    return resp

def get_read_status_for_kobo(ub_book_read):
    enum_to_string_map = {
        None: "ReadyToRead",
        ReadBook.STATUS_UNREAD: "ReadyToRead",
        ReadBook.STATUS_FINISHED: "Finished",
        ReadBook.STATUS_IN_PROGRESS: "Reading",
    }
    return enum_to_string_map[ub_book_read.read_status]


def get_statistics_response(statistics):
    resp = {
        "LastModified": convert_to_kobo_timestamp_string(statistics.date_updated),
    }
    if statistics.spent_reading_minutes:
        resp["SpentReadingMinutes"] = statistics.spent_reading_minutes
    if statistics.remaining_time_minutes:
        resp["RemainingTimeMinutes"] = statistics.remaining_time_minutes
    return resp


def get_current_bookmark_response(current_bookmark):
    resp = {
        "LastModified": convert_to_kobo_timestamp_string(current_bookmark.date_updated),
    }
    if current_bookmark.progress_percent:
        resp["ProgressPercent"] = current_bookmark.progress_percent
    if current_bookmark.content_source_progress_percent:
        resp["ContentSourceProgressPercent"] = current_bookmark.content_source_progress_percent
    if current_bookmark.location_value:
        resp["Location"] = {
            "Value": current_bookmark.location_value,
            "Type": current_bookmark.location_type,
            "Source": current_bookmark.location_source,
        }
    return resp
# Adds items to the given shelf.
def add_items_to_shelf(items, shelf):
    book_ids_already_in_shelf = set([book_shelf_links.book_id for book_shelf_links in shelf.book_shelf_links])
    items_unknown_to_calibre = []
    for item in items:
        try:
            if item["Type"] != "ProductRevisionTagItem":
                items_unknown_to_calibre.append(item)
                continue
            book_fetcher = FetchBookDetailsFromDB()
            book = book_fetcher.fetch_book_details_by_uuid(item["RevisionId"])
            #book = calibre_db.get_book_by_uuid(item["RevisionId"])
            if not book:
                items_unknown_to_calibre.append(item)
                continue

            book_id = book.id
            if book_id not in book_ids_already_in_shelf:
                shelf.Book.append(BookShelfLinks(book_id=book_id))
        except KeyError:
            items_unknown_to_calibre.append(item)
    return items_unknown_to_calibre


def NATIVE_KOBO_RESOURCES():
    return {
        "account_page": "https://secure.kobobooks.com/profile",
        "account_page_rakuten": "https://my.rakuten.co.jp/",
        "add_entitlement": "https://storeapi.kobo.com/v1/library/{RevisionIds}",
        "affiliaterequest": "https://storeapi.kobo.com/v1/affiliate",
        "audiobook_subscription_orange_deal_inclusion_url": "https://authorize.kobo.com/inclusion",
        "authorproduct_recommendations": "https://storeapi.kobo.com/v1/products/books/authors/recommendations",
        "autocomplete": "https://storeapi.kobo.com/v1/products/autocomplete",
        "blackstone_header": {"key": "x-amz-request-payer", "value": "requester"},
        "book": "https://storeapi.kobo.com/v1/products/books/{ProductId}",
        "book_detail_page": "https://store.kobobooks.com/{culture}/ebook/{slug}",
        "book_detail_page_rakuten": "https://Book.rakuten.co.jp/rk/{crossrevisionid}",
        "book_landing_page": "https://store.kobobooks.com/ebooks",
        "book_subscription": "https://storeapi.kobo.com/v1/products/books/subscriptions",
        "categories": "https://storeapi.kobo.com/v1/categories",
        "categories_page": "https://store.kobobooks.com/ebooks/categories",
        "category": "https://storeapi.kobo.com/v1/categories/{CategoryId}",
        "category_featured_lists": "https://storeapi.kobo.com/v1/categories/{CategoryId}/featured",
        "category_products": "https://storeapi.kobo.com/v1/categories/{CategoryId}/products",
        "checkout_borrowed_book": "https://storeapi.kobo.com/v1/library/borrow",
        "configuration_data": "https://storeapi.kobo.com/v1/configuration",
        "content_access_book": "https://storeapi.kobo.com/v1/products/books/{ProductId}/access",
        "customer_care_live_chat": "https://v2.zopim.com/widget/livechat.html?key=Y6gwUmnu4OATxN3Tli4Av9bYN319BTdO",
        "daily_deal": "https://storeapi.kobo.com/v1/products/dailydeal",
        "deals": "https://storeapi.kobo.com/v1/deals",
        "delete_entitlement": "https://storeapi.kobo.com/v1/library/{Ids}",
        "delete_tag": "https://storeapi.kobo.com/v1/library/tags/{TagId}",
        "delete_tag_items": "https://storeapi.kobo.com/v1/library/tags/{TagId}/items/delete",
        "device_auth": "https://storeapi.kobo.com/v1/auth/device",
        "device_refresh": "https://storeapi.kobo.com/v1/auth/refresh",
        "dictionary_host": "https://kbdownload1-a.akamaihd.net",
        "discovery_host": "https://discovery.kobobooks.com",
        "eula_page": "https://www.kobo.com/termsofuse?style=onestore",
        "exchange_auth": "https://storeapi.kobo.com/v1/auth/exchange",
        "external_book": "https://storeapi.kobo.com/v1/products/books/external/{Ids}",
        "facebook_sso_page":
            "https://authorize.kobo.com/signin/provider/Facebook/login?returnUrl=http://store.kobobooks.com/",
        "featured_list": "https://storeapi.kobo.com/v1/products/featured/{FeaturedListId}",
        "featured_lists": "https://storeapi.kobo.com/v1/products/featured",
        "free_books_page": {
            "EN": "https://www.kobo.com/{region}/{language}/p/free-ebooks",
            "FR": "https://www.kobo.com/{region}/{language}/p/livres-gratuits",
            "IT": "https://www.kobo.com/{region}/{language}/p/libri-gratuiti",
            "NL": "https://www.kobo.com/{region}/{language}/"
                  "List/bekijk-het-overzicht-van-gratis-ebooks/QpkkVWnUw8sxmgjSlCbJRg",
            "PT": "https://www.kobo.com/{region}/{language}/p/livros-gratis",
        },
        "fte_feedback": "https://storeapi.kobo.com/v1/products/ftefeedback",
        "get_tests_request": "https://storeapi.kobo.com/v1/analytics/gettests",
        "giftcard_epd_redeem_url": "https://www.kobo.com/{storefront}/{language}/redeem-ereader",
        "giftcard_redeem_url": "https://www.kobo.com/{storefront}/{language}/redeem",
        "help_page": "https://www.kobo.com/help",
        "kobo_audiobooks_enabled": "False",
        "kobo_audiobooks_orange_deal_enabled": "False",
        "kobo_audiobooks_subscriptions_enabled": "False",
        "kobo_nativeborrow_enabled": "True",
        "kobo_onestorelibrary_enabled": "False",
        "kobo_redeem_enabled": "True",
        "kobo_shelfie_enabled": "False",
        "kobo_subscriptions_enabled": "False",
        "kobo_superpoints_enabled": "False",
        "kobo_wishlist_enabled": "True",
        "library_book": "https://storeapi.kobo.com/v1/user/library/books/{LibraryItemId}",
        "library_items": "https://storeapi.kobo.com/v1/user/library",
        "library_metadata": "https://storeapi.kobo.com/v1/library/{Ids}/metadata",
        "library_prices": "https://storeapi.kobo.com/v1/user/library/previews/prices",
        "library_stack": "https://storeapi.kobo.com/v1/user/library/stacks/{LibraryItemId}",
        "library_sync": "https://storeapi.kobo.com/v1/library/sync",
        "love_dashboard_page": "https://store.kobobooks.com/{culture}/kobosuperpoints",
        "love_points_redemption_page":
            "https://store.kobobooks.com/{culture}/KoboSuperPointsRedemption?productId={ProductId}",
        "magazine_landing_page": "https://store.kobobooks.com/emagazines",
        "notifications_registration_issue": "https://storeapi.kobo.com/v1/notifications/registration",
        "oauth_host": "https://oauth.kobo.com",
        "overdrive_account": "https://auth.overdrive.com/account",
        "overdrive_library": "https://{libraryKey}.auth.overdrive.com/library",
        "overdrive_library_finder_host": "https://libraryfinder.api.overdrive.com",
        "overdrive_thunder_host": "https://thunder.api.overdrive.com",
        "password_retrieval_page": "https://www.kobobooks.com/passwordretrieval.html",
        "post_analytics_event": "https://storeapi.kobo.com/v1/analytics/event",
        "privacy_page": "https://www.kobo.com/privacypolicy?style=onestore",
        "product_nextread": "https://storeapi.kobo.com/v1/products/{ProductIds}/nextread",
        "product_prices": "https://storeapi.kobo.com/v1/products/{ProductIds}/prices",
        "product_recommendations": "https://storeapi.kobo.com/v1/products/{ProductId}/recommendations",
        "product_reviews": "https://storeapi.kobo.com/v1/products/{ProductIds}/reviews",
        "products": "https://storeapi.kobo.com/v1/products",
        "provider_external_sign_in_page":
            "https://authorize.kobo.com/ExternalSignIn/{providerName}?returnUrl=http://store.kobobooks.com/",
        "purchase_buy": "https://www.kobo.com/checkout/createpurchase/",
        "purchase_buy_templated": "https://www.kobo.com/{culture}/checkout/createpurchase/{ProductId}",
        "quickbuy_checkout": "https://storeapi.kobo.com/v1/store/quickbuy/{PurchaseId}/checkout",
        "quickbuy_create": "https://storeapi.kobo.com/v1/store/quickbuy/purchase",
        "rating": "https://storeapi.kobo.com/v1/products/{ProductId}/rating/{Rating}",
        "reading_state": "https://storeapi.kobo.com/v1/library/{Ids}/state",
        "redeem_interstitial_page": "https://store.kobobooks.com",
        "registration_page": "https://authorize.kobo.com/signup?returnUrl=http://store.kobobooks.com/",
        "related_items": "https://storeapi.kobo.com/v1/products/{Id}/related",
        "remaining_book_series": "https://storeapi.kobo.com/v1/products/books/series/{SeriesId}",
        "rename_tag": "https://storeapi.kobo.com/v1/library/tags/{TagId}",
        "review": "https://storeapi.kobo.com/v1/products/reviews/{ReviewId}",
        "review_sentiment": "https://storeapi.kobo.com/v1/products/reviews/{ReviewId}/sentiment/{Sentiment}",
        "shelfie_recommendations": "https://storeapi.kobo.com/v1/user/recommendations/shelfie",
        "sign_in_page": "https://authorize.kobo.com/signin?returnUrl=http://store.kobobooks.com/",
        "social_authorization_host": "https://social.kobobooks.com:8443",
        "social_host": "https://social.kobobooks.com",
        "stacks_host_productId": "https://store.kobobooks.com/collections/byproductid/",
        "store_home": "www.kobo.com/{region}/{language}",
        "store_host": "store.kobobooks.com",
        "store_newreleases": "https://store.kobobooks.com/{culture}/List/new-releases/961XUjtsU0qxkFItWOutGA",
        "store_search": "https://store.kobobooks.com/{culture}/Search?Query={query}",
        "store_top50": "https://store.kobobooks.com/{culture}/ebooks/Top",
        "tag_items": "https://storeapi.kobo.com/v1/library/tags/{TagId}/Items",
        "tags": "https://storeapi.kobo.com/v1/library/tags",
        "taste_profile": "https://storeapi.kobo.com/v1/products/tasteprofile",
        "update_accessibility_to_preview": "https://storeapi.kobo.com/v1/library/{EntitlementIds}/preview",
        "use_one_store": "False",
        "user_loyalty_benefits": "https://storeapi.kobo.com/v1/user/loyalty/benefits",
        "user_platform": "https://storeapi.kobo.com/v1/user/platform",
        "user_profile": "https://storeapi.kobo.com/v1/user/profile",
        "user_ratings": "https://storeapi.kobo.com/v1/user/ratings",
        "user_recommendations": "https://storeapi.kobo.com/v1/user/recommendations",
        "user_reviews": "https://storeapi.kobo.com/v1/user/reviews",
        "user_wishlist": "https://storeapi.kobo.com/v1/user/wishlist",
        "userguide_host": "https://kbdownload1-a.akamaihd.net",
        "wishlist_page": "https://store.kobobooks.com/{region}/{language}/account/wishlist",
    }

def check_shelf_edit_permissions(cur_shelf):
    if not cur_shelf.is_public and not cur_shelf.user_id == int(current_user.id):
        logger.error("User {} not allowed to edit shelf: {}".format(current_user.id, cur_shelf.name))
        return False
    if cur_shelf.is_public and not current_user.role_edit_shelfs():
        logger.info("User {} not allowed to edit public shelves".format(current_user.id))
        return False
    return True

async def make_calibre_web_auth_response(request: Request):
    # Get the JSON content from the request
    content = await request.json()
    
    # Generate tokens
    AccessToken = base64.b64encode(os.urandom(24)).decode('utf-8')
    RefreshToken = base64.b64encode(os.urandom(24)).decode('utf-8')
    
    # Create the response payload
    response_payload = {
        "AccessToken": AccessToken,
        "RefreshToken": RefreshToken,
        "TokenType": "Bearer",
        "TrackingId": str(uuid.uuid4()),
        "UserKey": content.get('UserKey', ""),
    }
    
    # Return the response
    return JSONResponse(content=response_payload)

async def delete_shelf_helper(cur_shelf):
    async with db_manager.get_session() as session:
        if not cur_shelf or not check_shelf_edit_permissions(cur_shelf):
            return False
        shelf_id = cur_shelf.id
        session.delete(cur_shelf)
        session.query(Shelf).filter(Shelf.shelf == shelf_id).delete()
        session.add(ShelfArchive(uuid=cur_shelf.uuid, user_id=cur_shelf.user_id))
        session.commit("successfully deleted Shelf {}".format(cur_shelf.name))
        return True
def check_shelf_view_permissions(cur_shelf):
    try:
        if cur_shelf.is_public:
            return True
        if current_user.is_anonymous or cur_shelf.user_id != current_user.id:
            logger.error("User is unauthorized to view non-public shelf: {}".format(cur_shelf.name))
            return False
    except Exception as e:
        logger.error(e)
    return True

def get_book_cover_with_uuid(book_uuid, resolution=None):
    book_fetcher = FetchBookDetailsFromDB()
    book = book_fetcher.fetch_book_details_by_uuid(book_uuid)
    if not book:
        return  # allows kobo.HandleCoverImageRequest to proxy request
    return get_book_cover_internal(book, resolution=resolution)
