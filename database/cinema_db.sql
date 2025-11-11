CREATE DATABASE cinema_db WITH ENCODING 'UTF8';
\c cinema_db;

CREATE TYPE discount_name as ENUM (
    'student',
    'school',
    'senior',
    'military'
);

CREATE TYPE ticket_type_name as ENUM (
    'standard',
    'reduced'
);

CREATE TYPE ticket_status AS ENUM (
    'used',
    'valid',
    'reserved',
    'payment_pending',
    'free'
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

CREATE TYPE shift_type as ENUM (
    'cashier',         
    'usher',                
    'cleaning',             
    'projection',           
    'technical_support'
);

CREATE TYPE payment_type as ENUM (
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

CREATE TABLE cinema (
    _id SERIAL PRIMARY KEY,
    fk_region_id INT NOT NULL,
    city VARCHAR(50), 
    street VARCHAR(50), 
    building_number INT CHECK (building_number > 0), 

    CONSTRAINT c_fk_region
        FOREIGN KEY (fk_region_id)
        REFERENCES region (_id)
        ON DELETE CASCADE 
);

CREATE TABLE "user" (
    _id SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL CHECK (char_length("name") > 0),
    surname VARCHAR(50) NOT NULL CHECK (char_length(surname) > 0),
    birthdate DATE NOT NULL CHECK (birthdate <= CURRENT_DATE),
    username VARCHAR(50) UNIQUE NOT NULL CHECK (char_length(username) >= 3),
    email VARCHAR(50) UNIQUE NOT NULL CHECK (email LIKE '%@%'),
    "password" VARCHAR(50) NOT NULL,
    account_create_date DATE NOT NULL CHECK (account_create_date <= CURRENT_DATE),
    last_login_time TIMESTAMP(0) DEFAULT NULL CHECK (
        last_login_time IS NULL OR 
        (last_login_time >= account_create_date AND last_login_time <= CURRENT_TIMESTAMP)
    )
);

CREATE TABLE regional_manager (
    _id INT PRIMARY KEY,

    CONSTRAINT c_fk_user_id
        FOREIGN KEY (_id)
        REFERENCES "user" (_id)
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
        ON DELETE RESTRICT,

    CONSTRAINT c_fk_manager_id
        FOREIGN KEY (fk_manager_id)
        REFERENCES regional_manager (_id)
        ON DELETE RESTRICT,
    
    CONSTRAINT term_date_check CHECK (end_date IS NULL OR end_date >= "start_date")
);

CREATE TABLE worker (
    _id SERIAL PRIMARY KEY,
    pesel_number VARCHAR(11) NOT NULL CHECK (char_length(pesel_number) = 11),
    bank_account_number VARCHAR(26) NOT NULL CHECK (char_length(bank_account_number) = 26),
    salary_month NUMERIC(10, 2) NOT NULL CHECK (salary_month > 0),

    CONSTRAINT fk_worker_user_id
        FOREIGN KEY (_id)
        REFERENCES "user"(_id)
        ON DELETE CASCADE
);

CREATE TABLE client (
    _id SERIAL PRIMARY KEY,

    CONSTRAINT c_fk_client_user_id
        FOREIGN KEY (_id)
        REFERENCES "user"(_id)
        ON DELETE CASCADE
);

CREATE TABLE payment (
    _id SERIAL PRIMARY KEY,
    fk_client_id INT,
    "type" payment_type NOT NULL,
    time_of_payment TIMESTAMP(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
        CHECK (time_of_payment <= CURRENT_TIMESTAMP),
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),

    CONSTRAINT c_fk_client_id
        FOREIGN KEY (fk_client_id)
        REFERENCES client (_id)
        ON DELETE SET NULL
);

CREATE TABLE movie (
    _id SERIAL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    director VARCHAR(50), 
    duration_minutes INT CHECK (duration_minutes > 0) 
);

CREATE TABLE "version" (
    _id SERIAL PRIMARY KEY,
    "language" languages NOT NULL, 
    subtitles languages NOT NULL,
    "format" movie_format NOT NULL  
);

CREATE TABLE movie_version (
    _id SERIAL PRIMARY KEY,
    fk_movie_id INT NOT NULL,
    fk_version_id INT NOT NULL,
    CONSTRAINT no_duplicate_movie_version 
        UNIQUE(fk_movie_id, fk_version_id),

    CONSTRAINT c_fk_movie
        FOREIGN KEY (fk_movie_id)
        REFERENCES movie (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_version
        FOREIGN KEY (fk_version_id)
        REFERENCES "version" (_id)
        ON DELETE CASCADE
);

CREATE TABLE license (
    _id INT PRIMARY KEY, 
    license_number INT NOT NULL UNIQUE,
    "start_date" DATE NOT NULL,
    end_date DATE NOT NULL,
    "cost"  NUMERIC(10,2) CHECK ("cost" > 0),
    CONSTRAINT license_date_check CHECK (end_date >= "start_date"),

    CONSTRAINT c_id
        FOREIGN KEY (_id)
        REFERENCES movie (_id)
        ON DELETE CASCADE
);

CREATE TABLE discount (
    _id SERIAL PRIMARY KEY,
    "name" discount_name NOT NULL,
    "percentage" NUMERIC(4,2) CHECK ("percentage" > 0 AND "percentage" < 100)    
);

CREATE TABLE special_offer (
    _id SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    start_time TIMESTAMP(0) NOT NULL,
    end_time TIMESTAMP(0),
    amount NUMERIC (10, 2) NOT NULL CHECK (amount > 0),

    CONSTRAINT special_offer_time_check CHECK (end_time IS NULL OR end_time > start_time)
);

CREATE TABLE ticket_type (
    _id SERIAL PRIMARY KEY,
    "name" ticket_type_name NOT NULL,
    price NUMERIC (10, 2) NOT NULL CHECK (price > 0)
);

CREATE TABLE product (
    _id SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    barcode VARCHAR(50) UNIQUE,
    price NUMERIC (10, 2) NOT NULL CHECK (price >= 0),
    is_available BOOLEAN NOT NULL
);

CREATE TABLE room (
    _id SERIAL PRIMARY KEY,
    fk_cinema_id INT NOT NULL, 
    "number" INT CHECK ("number" > 0),

    CONSTRAINT c_fk_cinema
        FOREIGN KEY (fk_cinema_id)
        REFERENCES cinema (_id)
        ON DELETE CASCADE
);

CREATE TABLE seat (
    _id SERIAL PRIMARY KEY,
    fk_room_id INT NOT NULL,
    seat_num INT NOT NULL CHECK (seat_num > 0),

    CONSTRAINT c_fk_room_id
        FOREIGN KEY (fk_room_id)
        REFERENCES room (_id)
        ON DELETE CASCADE
);

CREATE TABLE "service" (
    _id SERIAL PRIMARY KEY,

    CONSTRAINT c_fk_service_id
        FOREIGN KEY (_id) REFERENCES worker(_id)
        ON DELETE CASCADE
);

CREATE TABLE supervisor (
    _id SERIAL PRIMARY KEY,
    
    CONSTRAINT c_fk_supervisor_worker_id
        FOREIGN KEY (_id)
        REFERENCES worker(_id)
        ON DELETE CASCADE
);

CREATE TABLE employment (
    _id SERIAL PRIMARY KEY,
    fk_worker_id INT NOT NULL,
    fk_cinema_id INT NOT NULL,
    "start_date" DATE NOT NULL,
    end_date DATE,

    CONSTRAINT employment_date_check CHECK (end_date IS NULL OR end_date >= "start_date"),

    CONSTRAINT c_fk_employment_worker_id
        FOREIGN KEY (fk_worker_id)
        REFERENCES worker(_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_employment_cinema_id
        FOREIGN KEY (fk_cinema_id)
        REFERENCES cinema(_id)
        ON DELETE CASCADE
);

CREATE TABLE shift (
    _id SERIAL PRIMARY KEY,
    fk_worker_id INT NOT NULL,
    start_time TIMESTAMP(0) NOT NULL,
    end_time TIMESTAMP(0),
    "type" shift_type NOT NULL,

    CONSTRAINT c_fk_shift_worker_id
        FOREIGN KEY (fk_worker_id)
        REFERENCES worker(_id)
        ON DELETE CASCADE,

    CONSTRAINT shift_time_check CHECK (end_time IS NULL OR end_time > start_time)
);

CREATE TABLE screening (
    _id SERIAL PRIMARY KEY,
    fk_room_id INT NOT NULL,
    fk_movie_version_id INT NOT NULL,
    start_time TIMESTAMP(0) NOT NULL,
    end_time TIMESTAMP(0) NOT NULL,

    CONSTRAINT c_fk_room_id
        FOREIGN KEY (fk_room_id)
        REFERENCES room (_id)
        ON DELETE RESTRICT,

    CONSTRAINT c_fk_movie_version_id
        FOREIGN KEY (fk_movie_version_id)
        REFERENCES movie_version (_id)
        ON DELETE RESTRICT,

    CONSTRAINT screening_time_check CHECK (end_time > start_time)
);

CREATE TABLE ticket (
    _id SERIAL PRIMARY KEY,
    fk_ticket_type_id INT NOT NULL,
    fk_discount_id INT,
    fk_screening_id INT NOT NULL,
    fk_seat_id INT NOT NULL,
    fk_payment_id INT,
    qr_code VARCHAR(100) NOT NULL,
    "status" ticket_status NOT NULL DEFAULT 'free',
    price NUMERIC(10, 2) NOT NULL CHECK(price >= 0),

    CONSTRAINT c_fk_ticket_type_id
        FOREIGN KEY (fk_ticket_type_id)
        REFERENCES ticket_type (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_discount_id
        FOREIGN KEY (fk_discount_id)
        REFERENCES discount (_id),

    CONSTRAINT c_fk_screening_id
        FOREIGN KEY (fk_screening_id)
        REFERENCES screening (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_seat_id
        FOREIGN KEY (fk_seat_id)
        REFERENCES seat (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_payment_id
        FOREIGN KEY (fk_payment_id)
        REFERENCES payment (_id)
);

CREATE TABLE ticket_special_offer (
    fk_ticket_id INT NOT NULL,
    fk_special_offer_id INT NOT NULL,
    PRIMARY KEY (fk_ticket_id, fk_special_offer_id), 

    CONSTRAINT c_fk_ticket_id
        FOREIGN KEY (fk_ticket_id)
        REFERENCES ticket (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_special_offer_id
        FOREIGN KEY (fk_special_offer_id)
        REFERENCES special_offer (_id)
        ON DELETE CASCADE
);

CREATE TABLE product_sale (
    _id SERIAL PRIMARY KEY,
    fk_product_id INT NOT NULL,
    fk_payment_id INT NOT NULL,
    fk_cinema_id INT NOT NULL,
    price NUMERIC (10, 2) NOT NULL CHECK (price >= 0),

    CONSTRAINT c_fk_product_id
        FOREIGN KEY (fk_product_id)
        REFERENCES product (_id)
        ON DELETE RESTRICT,

    CONSTRAINT c_fk_payment_id
        FOREIGN KEY (fk_payment_id)
        REFERENCES payment (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_cinema_id
        FOREIGN KEY (fk_cinema_id)
        REFERENCES cinema (_id)
        ON DELETE RESTRICT
);

CREATE TABLE cinema_movie_version (
    fk_cinema_id INT NOT NULL,
    fk_movie_version_id INT NOT NULL,
    PRIMARY KEY (fk_cinema_id, fk_movie_version_id), 

    CONSTRAINT c_fk_cinema_id
        FOREIGN KEY (fk_cinema_id)
        REFERENCES cinema (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_movie_version_id
        FOREIGN KEY (fk_movie_version_id)
        REFERENCES movie_version (_id)
        ON DELETE CASCADE
);