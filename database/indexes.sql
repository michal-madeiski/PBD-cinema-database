-- DROP INDEX idx_cinema_city_lower;
-- DROP INDEX idx_screening_start_time_id;
-- DROP INDEX idx_ticket_price_zero;
-- DROP INDEX idx_shift_worker_time_covering;


CREATE INDEX idx_screening_fk_movie_version_id ON screening(fk_movie_version_id); --używane w q_12, q_13


-- --q_09
CREATE INDEX idx_screening_start_time_fk_room_id ON screening(start_time, fk_room_id);
CREATE INDEX idx_seat_screening_fk_screening_id ON ticket(fk_screening_id); --używane w q_21

-- --q_11
CREATE INDEX idx_product_sale_fk_payment_id ON product_sale(fk_payment_id);
CREATE INDEX idx_ticket_fk_payment_id ON ticket(fk_payment_id); --używane w q_23

-- --q_14
CREATE INDEX idx_shift_type ON shift(type);

-- --q_15
CREATE INDEX idx_worker_user_id ON worker(_id);
CREATE INDEX idx_employment_fk_worker_id ON employment(fk_worker_id);

-- --q_17
CREATE INDEX idx_screening_start_time_id ON screening(start_time, _id);

--q_18
CREATE INDEX idx_ticket_price_zero ON ticket(total_price) WHERE price = 0;

--q_19
CREATE INDEX idx_shift_worker_time_covering ON shift(fk_worker_id, start_time, end_time);


--q_21
CREATE INDEX idx_seat_room_id ON seat(fk_room_id);

--q_23
--korzysta z indeksu dla q_11
CREATE INDEX idx_payment_fk_client_id ON payment(fk_client_id);

--q_24
CREATE INDEX idx_cinema_city ON cinema(city);

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    indexname LIKE 'idx%'
ORDER BY
    schemaname,
    tablename;