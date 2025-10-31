CREATE DATABASE cinema_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE cinema_db;
CREATE TABLE Region(
    _id SERIAL PRIMARY KEY 
);
CREATE TYPE languages AS ENUM (
    'polish',
    'english',
    'spanish',
    'german' 
);
CREATE TYPE movie_format AS ENUM (
    '2D',
    '3D',
    'IMAX'
);
CREATE TABLE Movie(
    _id SERIAL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    director VARCHAR(50), 
    duration_minutes INT CHECK (duration_minutes>0) 
);
CREATE TABLE "Version"(
    _id SERIAL PRIMARY KEY,
    "language" languages NOT NULL, 
    subtitles languages NOT NULL,
    "format" movie_format NOT NULL  
);
CREATE TABLE Movie_version(
    _id SERIAL PRIMARY KEY,
    FK_movie_id INT NOT NULL,
    FK_version_id INT NOT NULL,
    CONSTRAINT no_duplicate_movie_version 
        UNIQUE(FK_movie_id, FK_version_id),

    CONSTRAINT fk_movie
        FOREIGN KEY (FK_movie_id)
        REFERENCES Movie (_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_version
        FOREIGN KEY (FK_version_id)
        REFERENCES "Version" (_id)
        ON DELETE CASCADE
);
CREATE TABLE LICENSE(
    _id INT PRIMARY KEY, 
    license_number INT NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    "cost"  NUMERIC(10,2) CHECK ("cost">0),
    CONSTRAINT license_date_check CHECK (start_date<end_date),

    CONSTRAINT fk_id
        FOREIGN KEY (_id)
        REFERENCES Movie (_id)
        ON DELETE CASCADE
);
CREATE TABLE Cinema(
    _id SERIAL PRIMARY KEY,
    FK_region_id INT NOT NULL,
    city VARCHAR(50), 
    street VARCHAR(50), 
    building_number INT CHECK (building_number > 0), 

    CONSTRAINT fk_region
        FOREIGN KEY (FK_region_id)
        REFERENCES Region (_id)
        ON DELETE CASCADE 
);
CREATE TABLE Cinema_movie(
    FK_cinema_id INT NOT NULL,
    FK_movie_id INT NOT NULL,
    PRIMARY KEY (FK_cinema_id, FK_movie_id), 

    CONSTRAINT fk_cinema
        FOREIGN KEY (FK_cinema_id)
        REFERENCES Cinema (_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_movie 
        FOREIGN KEY (FK_movie_id)
        REFERENCES Movie (_id)
        ON DELETE CASCADE
);
CREATE TABLE Room(
    _id SERIAL PRIMARY KEY,
    FK_cinema_id INT NOT NULL, 
    "number" INT CHECK ("number" > 0),

    CONSTRAINT fk_cinema
        FOREIGN KEY (FK_cinema_id)
        REFERENCES Cinema (_id)
        ON DELETE CASCADE
);
