--Room occupancy by month
SELECT
    EXTRACT(MONTH FROM screening.start_time) AS "Miesiąc",
    ROUND(
        100 * COUNT(ticket._id) FILTER (WHERE ticket.status = 'used')::NUMERIC /
            COALESCE(NULLIF(COUNT(ticket._id), 0), 1),
        2
        ) AS "Obłożenie w %"
FROM
    screening
LEFT JOIN ticket
    ON ticket.fk_screening_id = screening._id
WHERE 
    screening.start_time <= CURRENT_DATE
GROUP BY
    EXTRACT(MONTH FROM screening.start_time)
ORDER BY
    "Miesiąc";