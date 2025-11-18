--Workers with above-average employment time.
SELECT CONCAT(u.name, ' ', u.surname, ' (', u.username, ')') AS worker,
    ec.start_date,
    ec.years_worked
FROM worker w
    JOIN "user" u ON u._id = w._id
    JOIN (
        -- employment_current
        SELECT e.fk_worker_id AS worker,
            e.start_date,
            EXTRACT(
                YEAR
                FROM AGE(CURRENT_DATE, e.start_date)
            ) AS years_worked
        FROM employment e
        WHERE e.end_date IS NULL
    ) AS ec ON ec.worker = w._id
    CROSS JOIN (
        -- average_years
        SELECT AVG(
                EXTRACT(
                    YEAR
                    FROM AGE(e.end_date, e.start_date)
                )
            ) AS avg_years
        FROM employment e
        WHERE e.end_date IS NOT NULL
    ) AS ay
WHERE ec.years_worked > ay.avg_years
ORDER BY worker ASC;