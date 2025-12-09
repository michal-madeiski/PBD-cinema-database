-- BEGIN;
-- ALTER TYPE ticket_type_name ADD VALUE 'vip';
-- COMMIT; 

BEGIN;

INSERT INTO ticket_type (name, price) 
VALUES ('vip', 40);

ALTER TABLE ticket RENAME TO seat_screening; 

CREATE TABLE ticket (
    _id SERIAL PRIMARY KEY,
    _temp_legacy_id INT,
    fk_payment_id INT,
    fk_ticket_type_id INT,
    qr_code VARCHAR(100) NOT NULL,
    "status" ticket_status NOT NULL DEFAULT 'free',
    total_price FLOAT, 

    CONSTRAINT c_fk_payment_id
        FOREIGN KEY (fk_payment_id)
        REFERENCES payment (_id)
);


INSERT INTO ticket (
    fk_payment_id, 
    fk_ticket_type_id, 
    qr_code, 
    status, 
    total_price, 
    _temp_legacy_id 
)
SELECT 
    fk_payment_id, 
    fk_ticket_type_id, 
    qr_code, 
    status, 
    price, 
    _id 
FROM seat_screening
WHERE status IN ('used', 'valid', 'payment_pending', 'reserved');


ALTER TABLE seat_screening ADD COLUMN fk_ticket_id INT;


UPDATE seat_screening ss
SET fk_ticket_id = t._id
FROM ticket t
WHERE ss._id = t._temp_legacy_id;


ALTER TABLE seat_screening 
    ADD CONSTRAINT c_fk_ticket_id 
    FOREIGN KEY (fk_ticket_id) 
    REFERENCES ticket (_id) 
    ON DELETE SET NULL;


ALTER TABLE ticket_type RENAME TO seat_screening_type;


ALTER TABLE ticket_special_offer
    DROP CONSTRAINT ticket_special_offer_pkey,
    DROP CONSTRAINT c_fk_ticket_id;
    

UPDATE ticket_special_offer tso 
SET fk_ticket_id = t._id
FROM ticket t 
WHERE t._temp_legacy_id= tso.fk_ticket_id; 




ALTER TABLE ticket_special_offer
    ADD PRIMARY KEY (fk_ticket_id, fk_special_offer_id), 
    ADD CONSTRAINT c_fk_ticket_id
    FOREIGN KEY (fk_ticket_id)
    REFERENCES ticket (_id)
    ON DELETE CASCADE;

ALTER TABLE seat_screening
    DROP COLUMN fk_payment_id,
    DROP COLUMN qr_code,
    DROP COLUMN status; 
ALTER TABLE seat_screening
    RENAME COLUMN fk_ticket_type_id TO fk_seat_screening_type_id;  

CREATE TABLE ticket_type(
    _id SERIAL PRIMARY KEY, 
    name VARCHAR(100),
    percentage INT, 
    min_size INT
);

INSERT INTO ticket_type(name, percentage, min_size)
    VALUES('single', 0, 1); 

UPDATE ticket t
SET fk_ticket_type_id=tt._id
FROM ticket_type tt
WHERE tt.name='single'; 

ALTER TABLE ticket
    ADD CONSTRAINT c_fk_ticket_type_id 
    FOREIGN KEY (fk_ticket_type_id) 
    REFERENCES ticket_type (_id) 
    ON DELETE SET NULL;

ALTER TABLE ticket DROP COLUMN _temp_legacy_id;
COMMIT;