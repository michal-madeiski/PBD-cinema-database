CREATE DATABASE cinema_db WITH ENCODING 'UTF8';
\c cinema_db;

CREATE TYPE payment_type as ENUM(
    'cash',
    'card',
    'blik',
    'online',
    'voucher'
);

CREATE TABLE region (
    _id SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE regional_manager (
    _id INT PRIMARY KEY,

    CONSTRAINT c_fk_user_id
        FOREIGN KEY (_id)
        REFERENCES user (_id)
        ON DELETE CASCADE
);

CREATE TABLE term (
    _id SERIAL PRIMARY KEY,
    fk_region_id INT NOT NULL,
    fk_manager_id INT NOT NULL,
    "start_date" DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,

    CONSTRAINT c_fk_region_id
        FOREIGN KEY (fk_region_id)
        REFERENCES region (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_manager_id
        FOREIGN KEY (fk_manager_id)
        REFERENCES regional_manager (_id)
        ON DELETE CASCADE,

    CONSTRAINT date_check CHECK ("start_date" <= end_date)
);

CREATE TABLE product (
    _id SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    barcode VARCHAR(50) UNIQUE,
    price NUMERIC (10, 2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE payment (
    _id SERIAL PRIMARY KEY,
    fk_client_id INT NOT NULL,
    "type" payment_type NOT NULL,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),

    CONSTRAINT c_fk_client_id
        FOREIGN KEY (fk_client_id)
        REFERENCES client (_id)
        ON DELETE CASCADE
);

CREATE TABLE product_sale (
    _id SERIAL PRIMARY KEY,
    fk_product_id INT NOT NULL,
    fk_payment_id INT NOT NULL,
    fk_cinema_id INT NOT NULL,
    time_of_sale TIMESTAMP(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
        CHECK (time_of_sale <= CURRENT_TIMESTAMP),

    CONSTRAINT c_fk_product_id
        FOREIGN KEY (fk_product_id)
        REFERENCES product (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_payment_id
        FOREIGN KEY (fk_payment_id)
        REFERENCES payment (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_cinema_id
        FOREIGN KEY (fk_cinema_id)
        REFERENCES cinema (_id)
        ON DELETE CASCADE
);

CREATE TABLE screening (
    _id SERIAL PRIMARY KEY,
    fk_room_id INT NOT NULL,
    fk_movie_version_id INT NOT NULL,
    start_time TIMESTAMP(0),
    end_time TIMESTAMP(0),

    CONSTRAINT c_fk_room_id
        FOREIGN KEY (fk_room_id)
        REFERENCES room (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_movie_version_id
        FOREIGN KEY (fk_movie_version_id)
        REFERENCES movie_version (_id)
        ON DELETE CASCADE,

    CONSTRAINT check_time CHECK (start_time <= end_time)
);