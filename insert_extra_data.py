from db.db_manager.async_db_manager import AsyncDBManager
from db.classDefinitions.shelf import Shelf
from db.classDefinitions.book_shelf_links import BookShelfLinks
from db.classDefinitions.book_series import BookSeries
from db.classDefinitions.book_series_links import BookSeriesLinks
from db.classDefinitions.book_author_links import BookAuthorLinks

class DataInserter(AsyncDBManager):
    def __init__(self):
        super().__init__()

    async def insert_data(self):
        async with self.get_session() as session:
            try:
                # Insert data into shelves table
                shelf1 = Shelf(shelf_name='Shelf_1', kobo_should_sync=True, user_id=1)
                shelf2 = Shelf(shelf_name='Shelf_2', kobo_should_sync=False, user_id=1)
                session.add_all([shelf1, shelf2])

                # Insert data into book_shelf_links table
                book_shelf_links = [
                    BookShelfLinks(book_id=1, shelf_id=1),
                    BookShelfLinks(book_id=1, shelf_id=2),
                    BookShelfLinks(book_id=2, shelf_id=1),
                    BookShelfLinks(book_id=2, shelf_id=2),
                    BookShelfLinks(book_id=3, shelf_id=1),
                    BookShelfLinks(book_id=3, shelf_id=2),
                    BookShelfLinks(book_id=4, shelf_id=1),
                    BookShelfLinks(book_id=5, shelf_id=2),
                ]
                session.add_all(book_shelf_links)

                # Insert data into book_series table
                series1 = BookSeries(series_title='The Wheel of Time')
                series2 = BookSeries(series_title='The Stormlight Archive')
                session.add_all([series1, series2])

                # Insert data into book_series_links table
                book_series_links = [
                    BookSeriesLinks(book_id=1, book_series_id=1, number_in_series=2),
                    BookSeriesLinks(book_id=1, book_series_id=2, number_in_series=3),
                ]
                session.add_all(book_series_links)

                # Insert data into book_authors_links table
                book_authors_links = [
                    BookAuthorLinks(book_id=1, author_id=3),
                    BookAuthorLinks(book_id=1, author_id=2),
                    BookAuthorLinks(book_id=1, author_id=4),
                ]
                session.add_all(book_authors_links)

                await session.commit()
                print("Data inserted successfully")

            except Exception as e:
                await session.rollback()
                print(f"An error occurred: {e}")