-- Średnia liczba seansów dziennie na kino
WITH kino AS(
    SELECT cinema._id AS id, COUNT(screening._id)::numeric AS screening_count, COALESCE(MIN(screening.start_time)::DATE, DATE '2015-01-01') AS min_date
    FROM cinema
    LEFT JOIN room ON room.fk_cinema_id = cinema._id
    LEFT JOIN screening ON screening.fk_room_id = room._id
    GROUP BY cinema._id
)

SELECT cinema._id AS "Id kina", cinema.city AS "Miasto", cinema.street AS "Ulica", cinema.building_number AS "Nr budynku", ROUND(screening_count / GREATEST((CURRENT_DATE - min_date), 1), 2) AS "Średnia ilość seansów na dzień"
FROM kino
JOIN cinema ON kino.id = cinema._id
ORDER BY "Średnia ilość seansów na dzień" DESC;