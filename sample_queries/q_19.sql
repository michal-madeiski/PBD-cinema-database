--Employees with the most hours worked last month
EXPLAIN ANALYZE
SELECT u._id AS worker_id,
    u.name,
    u.surname,
    SUM(s.end_time - s.start_time) AS hours_of_work
FROM "user" u
    JOIN worker w ON w._id = u._id
    JOIN shift s ON s.fk_worker_id = w._id
WHERE s.start_time >= date_trunc('month', CURRENT_DATE - interval '1 month')
    AND s.start_time < date_trunc('month', CURRENT_DATE)
GROUP BY u._id
ORDER BY hours_of_work DESC;