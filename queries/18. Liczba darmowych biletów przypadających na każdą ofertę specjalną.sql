SELECT
    so._id AS special_offer_id,
    so.name,
    so.amount,
    COUNT(t._id) AS free_tickets_count
FROM special_offer so
LEFT JOIN ticket_special_offer tso ON tso.fk_special_offer_id = so._id
LEFT JOIN ticket t ON t._id = tso.fk_ticket_id AND t.price = 0
GROUP BY so._id
ORDER BY  so.amount DESC, free_tickets_count DESC;