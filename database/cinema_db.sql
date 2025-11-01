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
    "reduced",
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
    end_time TIMESTAMP(0) NOT NULL CHECK (start_time < end_time),
    amount NUMERIC (10, 2) NOT NULL CHECK (amount > 0)
};

CREATE TABLE ticket_type {
    _id SERIAL PRIMARY KEY,
    "name" ticket_type_name NOT NULL,
    price NUMERIC (10, 2) NOT NULL CHECK (price>0)
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