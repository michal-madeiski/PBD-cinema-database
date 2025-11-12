--Top 10 movie incomes.
WITH each_screening_income AS (
    SELECT
        s._id,
        s.fk_movie_version_id as version,
        SUM(t.price) FILTER (WHERE t.status <> 'free' AND t.status <> 'not_used') as screening_income
    FROM screening s
    JOIN ticket t ON t.fk_screening_id = s._id
    GROUP BY s._id
),
each_version_income AS (
    SELECT
        mv.fk_movie_id AS movie,
        SUM(esi.screening_income) as version_income
    FROM movie_version mv
    JOIN each_screening_income esi ON mv.fk_version_id = esi.version
    GROUP BY mv.fk_movie_id
)
SELECT
    m._id,
    m.title,
    SUM(evi.version_income) - l.cost as balance
FROM movie m
JOIN each_version_income evi ON m._id = evi.movie
JOIN license l ON l._id = m._id
GROUP BY m._id, m.title, l.cost
ORDER BY  balance DESC
LIMIT 10;