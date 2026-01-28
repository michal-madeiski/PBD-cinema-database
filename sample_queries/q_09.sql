--Cinema ranking by last month's ticket revenue.
--EXPLAIN ANALYZE
SELECT 
    cinema._id AS "Id kina",
    cinema.city || ', ul. ' || cinema.street || ' ' || cinema.building_number AS "Adres",
    COALESCE(SUM(seat_screening.price), 0) AS "Przychody z biletów"
FROM cinema
    LEFT JOIN room ON room.fk_cinema_id = cinema._id
    LEFT JOIN screening ON screening.fk_room_id = room._id
    AND screening.start_time >= (CURRENT_DATE - INTERVAL '1 month')
    AND screening.start_time < (CURRENT_DATE + INTERVAL '1 day')
    LEFT JOIN seat_screening ON seat_screening.fk_screening_id = screening._id
GROUP BY cinema._id
ORDER BY "Przychody z biletów" DESC;