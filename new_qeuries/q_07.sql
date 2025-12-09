--Product revenue vs ticket revenue
--EXPLAIN ANALYZE
SELECT 
    (
        SELECT 
            COALESCE(SUM(product_sale.price), 0)
        FROM 
            product_sale
    ) AS "Suma za produkty",
    (
        SELECT COALESCE(SUM(ticket.total_price), 0)
        FROM ticket
    ) AS "Suma za bilety";