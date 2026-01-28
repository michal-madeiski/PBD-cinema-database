--Region breakdown: cinema count, total revenue, revenue per cinema from last month's tickets.
--EXPLAIN ANALYZE
SELECT r._id AS region_id,
  r.name AS region_name,
  COUNT(DISTINCT c._id) AS cinemas_count,
  ROUND(SUM(ss.price), 2) AS total_ticket_revenue,
  ROUND(
    SUM(ss.price) / NULLIF(COUNT(DISTINCT c._id), 0),
    2
  ) AS revenue_per_cinema
FROM seat_screening ss
  JOIN screening s ON s._id = ss.fk_screening_id
  JOIN room rm ON rm._id = s.fk_room_id
  JOIN cinema c ON c._id = rm.fk_cinema_id
  JOIN region r ON r._id = c.fk_region_id
  JOIN ticket t ON t._id = ss.fk_ticket_id
WHERE t.status = 'used'
  AND s.start_time >= date_trunc('month', CURRENT_DATE - interval '1 month')
  AND s.start_time < date_trunc('month', CURRENT_DATE)
GROUP BY r._id
ORDER BY total_ticket_revenue DESC;