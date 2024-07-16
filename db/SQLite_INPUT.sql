-- SQLite
INSERT INTO book_series (id, series_title, date_added, date_updated)
VALUES (1, 'The Wheel of Time', '2019-01-01', '2019-01-01');
INSERT INTO book_series (id, series_title, date_added, date_updated)
VALUES (2, 'The Stormlight Archive', '2019-01-01', '2019-01-01');

INSERT INTO books_in_series (id, book_id, book_series_id, number_in_series)
VALUES (1, 1, 1, 2);
INSERT INTO books_in_series (id, book_id, book_series_id, number_in_series)
VALUES (2, 1, 2, 3);


-- -- SQLite
-- INSERT INTO authors (id, name, date_added, date_updated)
-- VALUES (2, 'SecondAuthor', '2019-01-01', '2019-01-01');
-- INSERT INTO authors (id, name, date_added, date_updated)
-- VALUES (3, 'ThirdAuthor', '2019-01-01', '2019-01-01');

-- INSERT INTO authors_in_books (id, author_id, book_id)
-- VALUES (2, 2, 1);
-- INSERT INTO authors_in_books (id, author_id, book_id)
-- VALUES (3, 3, 1);


-- SQLite
INSERT INTO shelves (id, shelf_name, kobo_should_sync, user_id)
VALUES (1, 'Shelf_1', '1', 1);
INSERT INTO shelves (id, shelf_name, kobo_should_sync, user_id)
VALUES (2, 'Shelf_2', '0', 1);

INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (1, 1, 1);
INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (2, 1, 2);
INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (3, 2, 1);
INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (4, 2, 2);
INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (5, 3, 1);
INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (6, 3, 2);
INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (7, 4, 1);
INSERT INTO book_shelf_links (id, book_id, shelf_id)
VALUES (8, 5, 2);