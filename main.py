from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import logging
from loguru import logger
from models.loguru_logger_setup import AppLogger, InterceptHandler
from db.admin_setup import create_admin_user
import sqlite3
import os
import shutil
import threading
from models.import_files_from_import_folder import FileImporter
from models.utils_path_manager import path_manager
from routers import (
    editBook_routers, 
    editAuthor_routers, 
    book_routers, 
    kobo_auth_routers, 
    search_routers,
    shelves_routers,
    authors_routers, 
    kobo_fast_api_routers,
    user_management_routers
)
from insert_extra_data import DataInserter
from db.db_manager.sync_db_manager import SyncDBManager
from werkzeug.security import generate_password_hash

# Set up logging
app_logger = AppLogger("AppLogger", "MyFastAPIApp", 'ERROR')

# Intercept logs from uvicorn
logging.getLogger("uvicorn").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]

# Intercept logs from SQLAlchemy
logging.getLogger("sqlalchemy.engine").handlers = [InterceptHandler()]
logging.getLogger("sqlalchemy").handlers = [InterceptHandler()]

# Define the version as a variable
api_version = "0.0.0.1"

# Configure CORS
origins = [
    "http://127.0.0.1:5656",  # The frontend origin
    "http://localhost:5656",
]

# Create the shared_info dictionary
shared_info = {
    "title": "FastAPI",
    "version": api_version,  # Use the variable here
    "description": "API for pylib",
    "summary": "API for pylib. Functions for managing, creating and working with the pylib backend",
}

db_file = path_manager.database_file_full_path
library_folder = path_manager.library_folder_full_path

def reset_data():
    if os.path.exists(db_file):
        os.remove(db_file)
    if os.path.exists(library_folder):
        shutil.rmtree(library_folder)

def import_files_background():
    importer = FileImporter()
    importer.process_all_imported_files()

def startup():
    create_tables = SyncDBManager()
    create_tables.create_fts_table()
    create_tables.create_tables()
    create_tables.set_relationships()    

def setup_background_tasks():
    # Start the import_files_background() method in a separate thread
    import_files_thread = threading.Thread(target=import_files_background)
    import_files_thread.start()

def insert_data():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    try:
        # Insert data into shelves table
        cursor.execute("INSERT INTO shelves (id, shelf_name, kobo_should_sync, user_id) VALUES (1, 'Shelf_1', '1', '1');")
        cursor.execute("INSERT INTO shelves (id, shelf_name, kobo_should_sync, user_id) VALUES (2, 'Shelf_2', '0', '1');")
        # Insert data into book_shelf_links table
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (1, 1, 1);")
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (2, 1, 2);")
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (3, 2, 1);")
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (4, 2, 2);")
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (5, 3, 1);")
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (6, 3, 2);")
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (7, 4, 1);")
        cursor.execute("INSERT INTO book_shelf_links (id, book_id, shelf_id) VALUES (8, 5, 2);")
        # Insert data into book_series table
        cursor.execute("INSERT INTO book_series (id, series_title, date_added, date_updated) VALUES (1, 'The Wheel of Time', '2019-01-01', '2019-01-01');")
        cursor.execute("INSERT INTO book_series (id, series_title, date_added, date_updated) VALUES (2, 'The Stormlight Archive', '2019-01-01', '2019-01-01');")
        # Insert data into book_series_links table
        cursor.execute("INSERT INTO book_series_links (id, book_id, book_series_id, number_in_series) VALUES (1, 1, 1, 2);")
        cursor.execute("INSERT INTO book_series_links (id, book_id, book_series_id, number_in_series) VALUES (2, 1, 2, 3);")
        # Insert data into book_authors_links table
        cursor.execute("INSERT INTO book_authors_links (id, book_id, author_id) VALUES (1, 1, 3);")
        cursor.execute("INSERT INTO book_authors_links (id, book_id, author_id) VALUES (2, 1, 2);")
        cursor.execute("INSERT INTO book_authors_links (id, book_id, author_id) VALUES (3, 1, 4);")
        connection.commit()
    except sqlite3.Error as e:
        logger.error(f"An error occurred: {e}")
    finally:
        connection.close()

def insert_file_location():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    try:
        # Update data in FileLocation kepub table
        cursor.execute("UPDATE file_location SET kepub_filename = 'kepub_filename' WHERE id = 1 AND book_id = 1;")
        cursor.execute("UPDATE file_location SET kepub_filename = 'kepub_filename' WHERE id = 2 AND book_id = 2;")
        cursor.execute("UPDATE file_location SET kepub_filename = 'kepub_filename' WHERE id = 3 AND book_id = 3;")
        cursor.execute("UPDATE file_location SET kepub_filename = 'kepub_filename' WHERE id = 4 AND book_id = 4;")
        cursor.execute("UPDATE file_location SET kepub_filename = 'kepub_filename' WHERE id = 5 AND book_id = 5;")
        cursor.execute("UPDATE file_location SET kepub_filename = 'kepub_filename' WHERE id = 6 AND book_id = 6;")
        cursor.execute("UPDATE file_location SET kepub_filename = 'kepub_filename' WHERE id = 7 AND book_id = 7;")
        connection.commit()
    except sqlite3.Error as e:
        logger.error(f"An error occurred: {e}")
    finally:
        connection.close()

clean_start = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    if clean_start:
        reset_data()
        startup()
        insert_data = DataInserter()
        await insert_data.insert_data()
        setup_background_tasks()
        insert_file_location()
    else:
        startup()
    create_admin_user()
    yield  # This allows FastAPI to run the application
    # Shutdown logic (if any)

app = FastAPI(lifespan=lifespan, **shared_info)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(editBook_routers.router)
app.include_router(editAuthor_routers.router)
app.include_router(book_routers.router)
app.include_router(search_routers.router)
app.include_router(shelves_routers.router)
app.include_router(authors_routers.router)
app.include_router(kobo_auth_routers.router)
app.include_router(kobo_fast_api_routers.router)
app.include_router(user_management_routers.router)

@app.get("/isOk", description="For checking if the API is running", summary="Checks if the API is running")
def root():
    return {"message": "All up and running!"}

# Use the shared_info dictionary to create openapi_schema and app
openapi_schema = get_openapi(routes=app.routes, **shared_info)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

