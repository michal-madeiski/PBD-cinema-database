--Ticket promotion breakdown
--EXPLAIN ANALYZE
WITH ticket_data AS (
    SELECT 
        fk_ticket_type_id,
        fk_discount_id,
        _id as ticket_id
    FROM ticket 
    WHERE status IN ('used', 'valid') 
),
aggregated AS (
    SELECT 
        tt.name AS ticket_type,
        CASE
            WHEN td.fk_discount_id IS NOT NULL AND tso.fk_special_offer_id IS NOT NULL 
                THEN 'discount + special offer'
            WHEN td.fk_discount_id IS NOT NULL AND tso.fk_special_offer_id IS NULL 
                THEN 'only discount'
            WHEN td.fk_discount_id IS NULL AND tso.fk_special_offer_id IS NOT NULL 
                THEN 'only special offer'
            ELSE 'none'
        END AS reductions_applied,
        COUNT(td.ticket_id) AS ticket_count
    FROM ticket_data td
    LEFT JOIN ticket_type tt ON td.fk_ticket_type_id = tt._id
    LEFT JOIN ticket_special_offer tso ON td.ticket_id = tso.fk_ticket_id
    GROUP BY tt.name, reductions_applied
),
total_count AS (
    SELECT SUM(ticket_count) as total FROM aggregated
)
SELECT 
    ticket_type,
    reductions_applied,
    ROUND(100.0 * ticket_count / total, 2) || '%' AS ticket_sale_percentage,
    ticket_count AS "count"
FROM aggregated, total_count
ORDER BY ticket_type, reductions_applied;