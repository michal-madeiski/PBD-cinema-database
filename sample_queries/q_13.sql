--Top 10 movie incomes.
--EXPLAIN ANALYZE
SELECT m._id,
    m.title,
    SUM(evi.version_income) - l.cost AS balance
FROM movie m
    JOIN (
        SELECT mv.fk_movie_id AS movie,
            SUM(esi.screening_income) AS version_income
        FROM movie_version mv
            JOIN (
                SELECT s._id,
                    s.fk_movie_version_id AS version,
                    SUM(t.price) FILTER (
                        WHERE t.status <> 'free'
                            AND t.status <> 'not_used'
                    ) AS screening_income
                FROM screening s
                    JOIN ticket t ON t.fk_screening_id = s._id
                GROUP BY s._id
            ) AS esi ON mv.fk_version_id = esi.version
        GROUP BY mv.fk_movie_id
    ) AS evi ON m._id = evi.movie
    JOIN license l ON l._id = m._id
GROUP BY m._id,
    m.title,
    l.cost
ORDER BY balance DESC
LIMIT 10;