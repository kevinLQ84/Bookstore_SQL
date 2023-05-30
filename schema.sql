DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS orders;

--authors
CREATE TABLE authors
--autoincrement creates a value for each entry in order of creation
(
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
    
);

INSERT INTO authors (name)
VALUES ('Just Kidding Rolling'),
        ('Geoff Kidney'),
        ('James Reginald Token'),
        ('Unknown');

--books

CREATE TABLE books

(   
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT
    
);

INSERT INTO books (author_id, title, price, description)
VALUES (1,'Harrison Bustler and The Public Room', 4.99, 'Epic adventure with epic worlds.'),
        (2,'Journal of The Muscle Man', 15.00, 'For those who wish to polish their muscles.'),
        (2,'Journal of The Muscle Man: Cat Years', 16.00, 'For those who wish to polish their muscles to fight cats.'),
        (3, 'A Gnome', 99.99, 'Contains a single page of a garden gnome, in a garden.'),
        (4,'Bookworms 3', 12.00, 'The third installment of the Bookworm series. It''ll worm into your mind! ');


--genres

CREATE TABLE genres
(   
    book_id INTEGER NOT NULL,
    genre_name TEXT NOT NULL
);

INSERT INTO genres (book_id, genre_name)
VALUES (1, 'Action'),
        (1, 'Fantasy'),
        (4, 'Fantasy'),
        (2, 'Sport'),
        (3, 'Sport'),
        (5, 'Education');


--users
CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL

);

INSERT INTO users (user_id, password)
--k password is 12
--v password is 12
--shopkeeper password is qwerty
VALUES ('k', 'pbkdf2:sha256:260000$Sm9qoaDKj74yP15u$9255b931ed1e1387eae9ca3ddcb34c5b87acba4a28f1ff03c141efbc0fc6f023'),
        ('j', 'pbkdf2:sha256:260000$Sm9qoaDKj74yP15u$9255b931ed1e1387eae9ca3ddcb34c5b87acba4a28f1ff03c141efbc0fc6f023'),
        ('shopkeeper', 'pbkdf2:sha256:260000$H0QBjaRFQMkB7jfl$3fc5af0f850be17e72714644cd6b35ad122018c8e1dcf2b2786c8abe4c700945');

--admins
CREATE TABLE admins
(
    user_id TEXT PRIMARY KEY
);

INSERT INTO admins (user_id)
VALUES ('shopkeeper');

--cart
--price represents total cost of the books
--used when in checkout
--order_id created and inserted by python
CREATE TABLE cart
(
    order_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL, 
    price REAL NOT NULL

);

INSERT INTO cart (order_id, user_id, book_id,quantity,price)
VALUES ('2', 'k', 1, 1, 4.10),
        ('2', 'k', 2, 1, 1.10);


--orders used to store for viewing by shopkeeper
CREATE TABLE orders
(
    order_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL, 
    price REAL NOT NULL,
    date TEXT NOT NULL

);
INSERT INTO orders (order_id, user_id, book_id, quantity, price, date)
VALUES ('1', 'k', 2, 1, 15.00, '2022-2-10');
        


