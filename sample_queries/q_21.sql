--Which seats are available for the given screening?
PREPARE q (int) AS
SELECT s.number as "seat number"
FROM seat s
    JOIN room r ON s.fk_room_id = r._id
    JOIN screening sc ON sc.fk_room_id = r._id
    JOIN ticket t ON t.fk_screening_id = sc._id
WHERE t.status = 'free'
    AND sc._id = $1
GROUP BY s._id
ORDER BY s.number ASC;
EXECUTE q(1236861);
--EXPLAIN ANALYZE EXECUTE q(1236861);