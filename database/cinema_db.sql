CREATE DATABASE cinema_db ENCODING = "UTF8";
\c cinema_db;

CREATE TYPE shift_type as ENUM (
    'ticket_sales',         -- sprzedaż biletów
    'concessions',          -- sprzedaż przekąsek
    'usher',                -- obsługa sali (wskazywanie miejsc, kontrola biletów)
    'cleaning',             -- sprzątanie sal
    'projection',           -- obsługa projektora i sprzętu
    'supervision',          -- nadzór / kierownik zmiany
    'event_support',        -- pomoc przy wydarzeniach specjalnych
    'technical_support'     -- pomoc techniczna (np. nagłośnienie)
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

CREATE TABLE client (
    _id SERIAL PRIMARY KEY,

    CONSTRAINT c_fk_client_user_id
        FOREIGN KEY (_id)
        REFERENCES "user"(_id)
        ON DELETE CASCADE
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

-- PLACEHOLDER BO ŻEBY SOBIE POTESTOWAĆ CINEMA ID
-- CREATE TABLE cinema (
--     _id SERIAL PRIMARY KEY,
--     name VARCHAR(50) NOT NULL
-- );

CREATE TABLE employment (
    _id SERIAL PRIMARY KEY,
    fk_worker_id INT NOT NULL,
    fk_cinema_id INT NOT NULL,
    "start_date" DATE NOT NULL,
    end_date DATE CHECK (end_date IS NULL OR end_date >= "start_date"),

    CONSTRAINT c_fk_employment_worker_id
        FOREIGN KEY (fk_worker_id)
        REFERENCES worker(_id)
        ON DELETE RESTRICT,

    CONSTRAINT c_fk_employment_cinema_id
        FOREIGN KEY (fk_cinema_id)
        REFERENCES cinema(_id)
        ON DELETE RESTRICT
);

CREATE TABLE shift (
    _id SERIAL PRIMARY KEY,
    fk_worker_id INT NOT NULL,
    start_time TIMESTAMP(0) NOT NULL,
    end_time TIMESTAMP(0) CHECK (end_time IS NULL OR end_time >= start_time),
    "type" shift_type NOT NULL,

    CONSTRAINT c_fk_shift_worker_id
        FOREIGN KEY (fk_worker_id)
        REFERENCES worker(_id)
        ON DELETE RESTRICT
);
