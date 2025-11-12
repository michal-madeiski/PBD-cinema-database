--Product revenue vs ticket revenue
SELECT 
(
    SELECT COALESCE(Sum(product_sale.price), 0)
    FROM product_sale
) AS "Produkty",

(
    SELECT COALESCE(Sum(ticket.price), 0)
    FROM ticket
) AS "Bilety";