SELECT v.format,
       COUNT(s._id) AS screenings
FROM version v
JOIN movie_version mv ON mv.fk_version_id = v._id
JOIN screening s ON s.fk_movie_version_id = mv._id
GROUP BY v.format
ORDER BY screenings DESC;