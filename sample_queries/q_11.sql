--Cash payments percentage: tickets, products, total.
SELECT ROUND((tp.cash_count / tp.total) * 100.0, 2) AS percent_tickets_cash,
    ROUND((pp.cash_count / pp.total) * 100.0, 2) AS percent_products_cash,
    ROUND(
        (
            (tp.cash_count + pp.cash_count) / (tp.total + pp.total)
        ) * 100.0,
        2
    ) AS percent_all_cash
FROM (
        SELECT COUNT(*)::numeric AS total,
            COUNT(*) FILTER (
                WHERE p.type = 'cash'
            )::numeric AS cash_count
        FROM ticket t
            JOIN payment p ON t.fk_payment_id = p._id
        WHERE t.fk_payment_id IS NOT NULL
    ) AS tp,
    (
        SELECT COUNT(*)::numeric AS total,
            COUNT(*) FILTER (
                WHERE p.type = 'cash'
            )::numeric AS cash_count
        FROM product_sale ps
            JOIN payment p ON ps.fk_payment_id = p._id
        WHERE ps.fk_payment_id IS NOT NULL
    ) AS pp;