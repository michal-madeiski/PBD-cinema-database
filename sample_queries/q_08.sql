--Average daily screenings per cinema
SELECT cinema._id AS "Id kina",
    cinema.city || ', ul. ' || cinema.street || ' ' || cinema.building_number AS "Adres",
    ROUND(
        COUNT(screening._id)::numeric / COALESCE(
            CURRENT_DATE - MIN(screening.start_time)::DATE + 1,
            1
        ),
        2
    ) AS "Średnia ilość seansów na dzień"
FROM cinema
    LEFT JOIN room ON room.fk_cinema_id = cinema._id
    LEFT JOIN screening ON screening.fk_room_id = room._id
    AND screening.start_time <= CURRENT_DATE
GROUP BY cinema._id
ORDER BY "Średnia ilość seansów na dzień" DESC;