SELECT *
FROM (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY u.account_create_date, c._id) AS row_number,
        u.*
    FROM client c
    JOIN "user" u ON u._id = c._id
) sub
WHERE row_number % 10000 = 0
ORDER BY row_number;
