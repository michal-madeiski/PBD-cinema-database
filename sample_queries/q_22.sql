--Which screenings are available in the given cinema?
PREPARE get_screening_details (int, date) AS
SELECT 
    m.title,
    TO_CHAR(s.start_time, 'HH24:MI') as start_time,
    TO_CHAR(s.end_time, 'HH24:MI') as end_time,
    v.language, 
    v.subtitles, 
    v.format
FROM 
    screening s
JOIN
    movie_version mv ON mv._id = s.fk_movie_version_id
JOIN
    movie m ON mv.fk_movie_id = m._id
JOIN
    "version" v ON mv.fk_version_id = v._id
JOIN
    room r ON s.fk_room_id = r._id
WHERE 
    r.fk_cinema_id = $1  
    AND DATE(s.start_time) = $2
ORDER BY 
    s.start_time;

EXECUTE get_screening_details(89, '2023-07-13');