--Ticket promotion breakdown
--EXPLAIN ANALYZE
WITH ticket_data AS (
    SELECT
        ss.fk_seat_screening_type_id AS type_id,
        ss.fk_discount_id AS discount_id,
        t._id AS ticket_id
    FROM seat_screening ss
    JOIN ticket t ON ss.fk_ticket_id = t._id
    WHERE t.status IN ('used', 'valid')
),
aggregated AS (
    SELECT 
        st.name AS ticket_type,
        CASE
            WHEN discount_id IS NOT NULL 
                 AND tso.fk_special_offer_id IS NOT NULL THEN 'discount + special offer'
            WHEN discount_id IS NOT NULL 
                 AND tso.fk_special_offer_id IS NULL THEN 'only discount'
            WHEN discount_id IS NULL 
                 AND tso.fk_special_offer_id IS NOT NULL THEN 'only special offer'
            ELSE 'none'
        END AS reductions_applied,
        COUNT(td.ticket_id) AS ticket_count
    FROM ticket_data td
    LEFT JOIN seat_screening_type st 
           ON td.type_id = st._id
    LEFT JOIN ticket_special_offer tso 
           ON td.ticket_id = tso.fk_ticket_id
    GROUP BY st.name, reductions_applied
),
total_count AS (
    SELECT SUM(ticket_count) AS total
    FROM aggregated
)
SELECT 
    ticket_type,
    reductions_applied,
    ROUND(100.0 * ticket_count / total, 2) || '%' AS ticket_sale_percentage,
    ticket_count AS "count"
FROM aggregated, total_count
ORDER BY ticket_type, reductions_applied;
