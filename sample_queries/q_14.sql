--Overall number of workers per shift type in each cinema.
SELECT
    CONCAT(c.city, ', ', c.street, ' ', c.building_number) AS cinema_address,
    COUNT(s.fk_worker_id) FILTER (WHERE s.type = 'cashier') AS cashier_count,
    COUNT(s.fk_worker_id) FILTER (WHERE s.type = 'usher') AS usher_count,
    COUNT(s.fk_worker_id) FILTER (WHERE s.type = 'cleaning') AS cleaning_count,
    COUNT(s.fk_worker_id) FILTER (WHERE s.type = 'projection') AS projection_count,
    COUNT(s.fk_worker_id) FILTER (WHERE s.type = 'technical_support') AS technical_support_count
FROM cinema c
JOIN employment e ON e.fk_cinema_id = c._id
JOIN worker w ON w._id = e.fk_worker_id
JOIN shift s ON s.fk_worker_id = w._id
GROUP BY c._id
ORDER BY cinema_address ASC;