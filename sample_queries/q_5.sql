--Ticket promotion breakdown
SELECT tt.name AS ticket_type,
CASE 
	WHEN t.fk_discount_id IS NOT NULL AND tso.fk_special_offer_id IS NOT NULL THEN 'discount + special offer'
	WHEN t.fk_discount_id IS NOT NULL AND tso.fk_special_offer_id IS NULL THEN 'only discount'
	WHEN t.fk_discount_id IS NULL AND tso.fk_special_offer_id IS NOT NULL THEN 'only special offer'
	ELSE 'none'
END AS reductions_applied,
ROUND(100.0 * COUNT(DISTINCT t._id) / SUM(COUNT(DISTINCT t._id)) OVER (), 2) || '%' AS ticket_sale_percentage,
COUNT(DISTINCT t._id) AS "count"
FROM ticket t
LEFT JOIN ticket_type tt ON t.fk_ticket_type_id = tt._id
LEFT JOIN ticket_special_offer tso ON tso.fk_ticket_id = t._id
WHERE t.status IN ('used', 'valid')
GROUP BY tt.name, reductions_applied
ORDER BY tt.name, reductions_applied;