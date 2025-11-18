--Workers with above-average employment time.
WITH employment_current AS (
    SELECT e.fk_worker_id worker,
        e.start_date,
        EXTRACT(
            YEAR
            FROM AGE(CURRENT_DATE, e.start_date)
        ) AS years_worked
    FROM employment e
    WHERE e.end_date IS NULL
),
average_years AS (
    SELECT AVG(
            EXTRACT(
                YEAR
                FROM AGE(e.end_date, e.start_date)
            )
        ) as avg_years
    FROM employment e
    WHERE e.end_date IS NOT NULL
)
SELECT CONCAT(u.name, ' ', u.surname, ' (', u.username, ')') as worker,
    ec.start_date,
    ec.years_worked
FROM worker w
    JOIN "user" u ON u._id = w._id
    JOIN employment_current ec ON ec.worker = w._id
    CROSS JOIN average_years ay
WHERE ec.years_worked > ay.avg_years
ORDER BY worker ASC;