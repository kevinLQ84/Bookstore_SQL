--check to see if data exists
SELECT * 
FROM authors;

SELECT * 
FROM books;

--selects name and titles of an author
SELECT name, title
FROM authors JOIN books
ON authors.author_id = books.author_id
--id corresponds to author
WHERE name='Geoff Kidney';

--find books with author id of 2
SELECT * 
FROM authors JOIN books
ON authors.author_id = books.author_id
WHERE books.author_id = 2;

--check genres
SELECT * 
FROM genres;

--search genre
SELECT *
FROM authors 
JOIN books
JOIN genres
ON authors.author_id = books.author_id
AND genres.book_id = books.book_id
WHERE genre_name = 'Sport';

--search genre and name
SELECT *
FROM authors 
JOIN books
JOIN genres
ON authors.author_id = books.author_id
AND genres.book_id = books.book_id
WHERE genre_name = 'Education'
AND title LIKE '%bo%';

SELECT *
FROM authors 
JOIN books
JOIN genres
ON authors.author_id = books.author_id
AND genres.book_id = books.book_id
WHERE books.title LIKE '%harr%';

--SELECTS JOINED BOOKS, need distinct
SELECT DISTINCT books.title, authors.name, books.price, books.description
FROM authors 
JOIN books
JOIN genres
ON authors.author_id = books.author_id
AND genres.book_id = books.book_id;

--find book and its genre
SELECT books.title, genres.genre_name
FROM books JOIN genres
ON books.book_id=genres.book_id
WHERE books.book_id = 1;

--find most recent order id
SELECT MAX(order_id)
FROM orders;

--check cart
SELECT *
FROM cart;

--check orders
SELECT *
FROM orders
ORDER BY date DESC;

--check total of an order
SELECT user_id, order_id, SUM(price)
FROM orders
GROUP BY order_id;

--users
SELECT *
FROM users;

--disticnt genre names
SELECT DISTINCT genre_name FROM genres 
ORDER BY genre_name ASC;

--check cart of id
SELECT *
FROM cart
WHERE user_id = 'k';

--update a book
UPDATE books
SET price = '4.98'
WHERE book_id = 1;

SELECT title 
FROM books
WHERE title = 'genre_name';

SELECT DISTINCT books.title, authors.name, books.price, books.description
FROM authors 
JOIN books
JOIN genres
ON authors.author_id = books.author_id
AND genres.book_id = books.book_id
WHERE books.book_id = 10;

SELECT *
FROM books
WHERE book_id = 6;

SELECT books.price
FROM books
JOIN cart
ON books.book_id = cart.book_id
WHERE cart.book_id = 1;

UPDATE cart
SET price = 10
WHERE book_id = 1
AND user_id = 'k';

--select unique order order id and user id pairs
SELECT
   user_id, MAX(order_id) AS latest_order_id
FROM
    (
    SELECT user_id, order_id
    FROM cart
    UNION
    SELECT user_id, order_id
    FROM orders
    );
   
--find shopkeepers
SELECT *
FROM admins
WHERE user_id = 'shopkeeper';

SELECT book_id
FROM books
WHERE author_id = 1
AND title = 'wqe';

--update a user_id
UPDATE users 
SET user_id = 'c'
WHERE user_id = 'k';
UPDATE cart 
SET user_id = 'c'
WHERE user_id = 'k';
UPDATE orders 
SET user_id = 'c'
WHERE user_id = 'k';

SELECT COUNT(DISTINCT order_id) AS num_order
FROM orders
WHERE user_id = 'k';

--get specific book columns
SELECT DISTINCT books.title, authors.name, books.price, books.description
FROM authors 
JOIN books
JOIN genres
ON authors.author_id = books.author_id
AND genres.book_id = books.book_id
WHERE books.book_id = 17;

SELECT COUNT(DISTINCT order_id) AS num_order
FROM orders
WHERE user_id = 'k';

SELECT MAX(order_id) AS latest_order_id
FROM
(
SELECT user_id, order_id
FROM cart
UNION
SELECT user_id, order_id
FROM orders
);