--Regional managers who managed 3 or more regions
SELECT u._id AS regional_manager_id,
    u.name,
    u.surname,
    COUNT(r._id) AS number_of_regions
FROM "user" u
    JOIN regional_manager rm ON rm._id = u._id
    JOIN term t ON t.fk_manager_id = rm._id
    JOIN region r ON r._id = t.fk_region_id
GROUP BY u._id
HAVING COUNT(r._id) >= 3
ORDER BY number_of_regions DESC