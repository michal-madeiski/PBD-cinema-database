CREATE DATABASE cinema_db ENCODING = "UTF8";
\c cinema_db;


CREATE TYPE discount_name as ENUM {
    "student",
    "school",
    "senior",
    "military"
};

CREATE TYPE ticket_type_name as ENUM {
    "standard",
    "reduced"
};

CREATE TYPE ticket_status AS ENUM (
    "used",
    "valid",
    "reserved",
    "payment_pending",
    "free"
);

CREATE TABLE discount {
    _id SERIAL PRIMARY KEY,
    "name" discount_name NOT NULL,
    "percentage" NUMERIC(4,2) CHECK ("percentage" > 0 AND "percentage" < 100)    
};

CREATE TABLE special_offer {
    _id SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    start_time TIMESTAMP(0) NOT NULL,
    end_time TIMESTAMP(0) CHECK (end_time IS NULL OR start_time < end_time),
    amount NUMERIC (10, 2) NOT NULL CHECK (amount > 0)
};

CREATE TABLE ticket_type {
    _id SERIAL PRIMARY KEY,
    "name" ticket_type_name NOT NULL,
    price NUMERIC (10, 2) NOT NULL CHECK (price > 0)
}

CREATE TABLE seat {
    _id SERIAL PRIMARY KEY,
    fk_room_id INT NOT NULL,
    seat_num INT NOT NULL CHECK (seat_num > 0),

    CONSTRAINT c_fk_room_id
        FOREIGN KEY (fk_room_id)
        REFERENCES room (_id)
        ON DELETE CASCADE
};

CREATE TABLE ticket {
    _id SERIAL PRIMARY KEY,
    fk_ticket_type_id INT NOT NULL,
    fk_discount_id INT,
    fk_screening_id INT NOT NULL,
    fk_seat_id INT NOT NULL,
    fk_payment_id INT,
    qr_code VARCHAR(100) NOT NULL,
    status ticket_status NOT NULL DEFAULT "free"

    CONSTRAINT c_fk_ticket_type_id
        FOREIGN KEY (fk_ticket_type_id)
        REFERENCES ticket_type (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_discount_id
        FOREIGN KEY (fk_discount_id)
        REFERENCES discount (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_screening_id
        FOREIGN KEY (fk_screening_id)
        REFERENCES screening (_id)
        ON DELETE CASCADE,

    CONSTRAINT c_fk_seat_id
        FOREIGN KEY (fk_seat_id)
        REFERENCES seat (_id)
        ON DELETE CASCADE

    CONSTRAINT c_fk_payment_id
        FOREIGN KEY (fk_payment_id)
        REFERENCES payment (_id)
        ON DELETE CASCADE
};

CREATE TABLE ticket_special_offer {
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
};

CREATE TYPE shift_type as ENUM (
    "cashier",         
    "usher",                
    "cleaning",             
    "projection",           
    "technical_support"
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
