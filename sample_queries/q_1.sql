--Number of tickets sold per movie
SELECT m._id, m.title, COUNT t._id AS tickets_sold
FROM ticket t
JOIN screening s ON t.fk_screening_id = s._id
JOIN movie_version mv ON s.fk_movie_version_id = mv._id
JOIN movie m ON mv.fk_movie_id = m._id
WHERE t.status IN ('used', 'valid')
GROUP BY m.title
ORDER BY tickets_sold DESC; 