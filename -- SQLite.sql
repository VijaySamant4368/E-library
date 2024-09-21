-- SQLite
SELECT * FROM users;

.schema

-- SELECT * from users;

-- DROP TABLE books;

-- CREATE TABLE books (
--     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
--     name TEXT,
--     uploader_id INTEGER, 
--     cover BLOB ,
--     book BLOB ,
--     FOREIGN KEY (uploader_id) REFERENCES users(id)
-- );

-- INSERT INTO books (id, name, author, genre) VALUES (0, "None", "No-one", "None");

-- SELECT * from books;

-- DELETE from owners;
-- INSERT INTO owners (owner_id, book_id) values (3, 0);

-- DROP TABLE books;


-- CREATE TABLE authors (
--     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
--     name TEXT,
--     about Text
-- );

-- DROP TABLE genres;

-- CREATE TABLE genres (
--     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
--     name TEXT,  
--     about Text
-- );

-- CREATE TABLE bookGenres (
--     book_id INTEGER,
--     genre_id INTEGER,
--     PRIMARY KEY (book_id, genre_id),
    
--     FOREIGN KEY (book_id) REFERENCES books(id),
--     FOREIGN KEY (genre_id) REFERENCES genres(id)
-- );

-- DELETE FROM books;

-- DELETE FROM genres
-- WHERE ROWID NOT IN 
-- (
--     SELECT MIN(ROWID)
--     FROM genres
--     GROUP BY name
-- );

-- delete from books;    
-- delete from sqlite_sequence where name='books';
-- delete from bookGenres;    
-- delete from sqlite_sequence where name='bookGenres';
delete from books;    
delete from sqlite_sequence where name='books';



-- delete from genres;
-- delete from sqlite_sequence where name='genres';
-- INSERT INTO genres (name, about) values ("comedy", "Comedy is a genre of fiction that consists of discourses or works intended to be humorous or amusing by inducing laughter, especially in theatre, film, stand-up comedy, television, radio, books, or any other entertainment medium.");

-- INSERT INTO genres (name, about) values ("adventure", "An adventure is an event or series of events that happens outside the course of the protagonist's ordinary life, usually accompanied by danger, often by physical action.");

-- INSERT INTO genres (name, about) values ("fantasy", "In popular culture, the fantasy genre predominantly features settings that emulate Earth, but with a sense of otherness. In its broadest sense, however, fantasy consists of works by many writers, artists, filmmakers, and musicians from ancient myths and legends to many recent and popular works.");

-- CREATE TABLE bookAuthors (
--     book_id INTEGER,
--     author_id INTEGER,
--     PRIMARY KEY (book_id, author_id),
    
--     FOREIGN KEY (book_id) REFERENCES books(id),
--     FOREIGN KEY (author_id) REFERENCES authors(id)
-- );

-- SELECT * from genres;
SELECT id, name FROM books;
-- DELETE FROM owners;
-- SELECT * FROM bookGenres;
-- SELECT * FROM bookAuthors;

-- PRAGMA page_count;
-- PRAGMA page_size;

-- VACUUM;