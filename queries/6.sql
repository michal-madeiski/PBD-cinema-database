-- 10 najczęściej sprzedawanych produktów
SELECT product.name AS "Nazwa", Count(product_sale._id) AS "Sprzedanych"
FROM product
LEFT JOIN product_sale ON product_sale.fk_product_id = product._id
GROUP BY product.name
ORDER BY "Sprzedanych" DESC
LIMIT 10;