--Total ticket revenue per cinema from the last year
--EXPLAIN ANALYZE
SELECT c._id,
    c.city,
    c.street,
    c.building_number,
    SUM(t.price) AS total_ticket_income
FROM cinema c
    FULL JOIN room r ON r.fk_cinema_id = c._id
    JOIN screening s ON s.fk_room_id = r._id
    JOIN ticket t ON t.fk_screening_id = s._id
WHERE s.start_time >= (CURRENT_DATE - INTERVAL '1 year')
GROUP BY c._id
ORDER BY total_ticket_income DESC;