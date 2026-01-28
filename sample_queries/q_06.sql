--Top 10 best-selling products.
--EXPLAIN ANALYZE
SELECT 
    product.name AS "Nazwa", 
    COUNT(product_sale._id) AS "Sprzedanych"
FROM product
    LEFT JOIN product_sale ON product_sale.fk_product_id = product._id
GROUP BY product.name
ORDER BY "Sprzedanych" DESC
LIMIT 10;