--Region breakdown: cinema count, total revenue, revenue per cinema from last month's tickets
SELECT
    r._id AS region_id,
    r.name AS region_name,
    COUNT(DISTINCT c._id) AS cinemas_count,
    ROUND(SUM(t.price), 2) AS total_ticket_revenue,
    ROUND(SUM(t.price) / NULLIF(COUNT(DISTINCT c._id), 0), 2) AS revenue_per_cinema
FROM ticket t
JOIN screening s ON s._id = t.fk_screening_id
JOIN room rm ON rm._id = s.fk_room_id
JOIN cinema c ON c._id = rm.fk_cinema_id
JOIN region r ON r._id = c.fk_region_id
WHERE t.status = 'used'
  AND s.start_time >= date_trunc('month', CURRENT_DATE - interval '1 month')
  AND s.start_time <  date_trunc('month', CURRENT_DATE)
GROUP BY r._id
ORDER BY total_ticket_revenue DESC;
