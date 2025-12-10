--Drop invalid indexes:
-- DROP INDEX idx_cinema_city_lower;
-- DROP INDEX idx_screening_start_time_id;
-- DROP INDEX idx_ticket_price_zero;
-- DROP INDEX idx_shift_worker_time_covering;


--Create indexes after alter:
-- CREATE INDEX idx_screening_fk_movie_version_id ON screening(fk_movie_version_id);
-- CREATE INDEX idx_screening_start_time_fk_room_id ON screening(start_time, fk_room_id);
-- CREATE INDEX idx_seat_screening_fk_screening_id ON seat_screening(fk_screening_id);
-- CREATE INDEX idx_product_sale_fk_payment_id ON product_sale(fk_payment_id);
-- CREATE INDEX idx_ticket_fk_payment_id ON ticket(fk_payment_id);
-- CREATE INDEX idx_ticket_fk_payment_id_id ON ticket(fk_payment_id, _id);
-- CREATE INDEX idx_shift_type ON shift(type);
-- CREATE INDEX idx_worker_user_id ON worker(_id);
-- CREATE INDEX idx_employment_fk_worker_id ON employment(fk_worker_id);
-- CREATE INDEX idx_screening_start_time_id ON screening(start_time, _id);
-- CREATE INDEX idx_ticket_price_zero ON ticket(total_price) WHERE total_price = 0;
-- CREATE INDEX idx_shift_worker_time_covering ON shift(fk_worker_id, start_time, end_time);
-- CREATE INDEX idx_seat_room_id ON seat(fk_room_id);
-- CREATE INDEX idx_payment_fk_client_id ON payment(fk_client_id);
-- CREATE INDEX idx_cinema_city ON cinema(city);
-- CREATE INDEX idx_seat_screening_fk_ticket_id ON seat_screening(fk_ticket_id);


--Print created indexes:
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