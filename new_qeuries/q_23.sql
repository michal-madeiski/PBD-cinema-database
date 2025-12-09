--Client's ticket history.
--EXPLAIN ANALYZE
SELECT
    movie.title AS "Tytuł",
    cinema.city || ', ul. ' || cinema.street || ' ' || cinema.building_number AS "Adres kina",
    screening.start_time::DATE AS "Data",
    screening.start_time::TIME AS "Godzina",
    room.number AS "Sala",
    seat.number AS "Miejsce",
    ticket.status AS "Status",
    seat_screening.price AS "Cena"
FROM seat_screening
    JOIN tciket ON seat_screening.fk_ticket_id = ticket._id
    JOIN screening ON screening._id = seat_screening.fk_screening_id
    JOIN movie_version ON movie_version._id = screening.fk_movie_version_id
    JOIN movie ON movie._id = movie_version.fk_movie_id
    JOIN room ON room._id = screening.fk_room_id
    JOIN cinema ON cinema._id = room.fk_cinema_id
    JOIN seat ON seat._id = seat_screening.fk_seat_id
    JOIN payment ON payment._id = ticket.fk_payment_id
WHERE payment.fk_client_id = 260921
ORDER BY screening.start_time ASC;