--Number of tickets sold per movie
SELECT m._id,
    m.title,
    COUNT (DISTINCT ss.fk_ticket_id) AS tickets_sold
FROM seat_screening ss
    JOIN ticket t ON t._id = ss.fk_ticket_id
    JOIN screening s ON ss.fk_screening_id = s._id
    JOIN movie_version mv ON s.fk_movie_version_id = mv._id
    JOIN movie m ON mv.fk_movie_id = m._id
WHERE t.status IN ('valid', 'used')
GROUP BY m._id,
    m.title
ORDER BY tickets_sold DESC;