--Cinemas in city.
EXPLAIN
SELECT c._id AS cinema_id,
    c.city,
    r.name AS region_name,
    c.street,
    c.building_number
FROM cinema c
    JOIN region r ON r._id = c.fk_region_id
WHERE LOWER(c.city) = 'świdnica'
ORDER BY c._id