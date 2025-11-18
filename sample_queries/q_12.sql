--Most screened version for each movie.
WITH movie_version_screening_count AS (
    SELECT mv.fk_movie_id,
        mv.fk_version_id,
        COUNT(s._id) AS screening_count
    FROM screening s
        JOIN movie_version mv ON s.fk_movie_version_id = mv._id
    GROUP BY mv.fk_movie_id,
        mv.fk_version_id
),
movie_screening_max AS (
    SELECT fk_movie_id,
        MAX(screening_count) as max_screening_count
    FROM movie_version_screening_count
    GROUP BY fk_movie_id
)
SELECT m._id,
    m.title,
    v.language,
    v.format,
    mvsc.screening_count
FROM movie_version_screening_count mvsc
    JOIN movie_screening_max msm ON mvsc.fk_movie_id = msm.fk_movie_id
    AND mvsc.screening_count = msm.max_screening_count
    JOIN movie m ON mvsc.fk_movie_id = m._id
    JOIN version v ON mvsc.fk_version_id = v._id
ORDER BY mvsc.screening_count DESC,
    m.title ASC