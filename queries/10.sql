-- Obłożenie sal w zależności od miesiąca
WITH room_seats AS (
  SELECT room._id AS room_id, COUNT(seat._id) AS seat_count
  FROM room
  LEFT JOIN seat ON seat.fk_room_id = room._id
  GROUP BY room._id
),
cap_per_month AS (
  SELECT to_char(screening.start_time, 'MM') AS month,
        SUM(room_seats.seat_count) AS capacity
  FROM screening
  JOIN room_seats ON room_seats.room_id = screening.fk_room_id
  GROUP BY month
),
sold_per_month AS (
  SELECT to_char(screening.start_time, 'MM') AS month,
        COUNT(ticket._id) AS sold
  FROM screening
  LEFT JOIN ticket ON ticket.fk_screening_id = screening._id
    AND ticket.status = 'used'
  GROUP BY month
)
SELECT
  cap_per_month.month AS "Miesiąc",
  ROUND(100.0 * COALESCE(sold_per_month.sold, 0) / NULLIF(cap_per_month.capacity, 0), 2) AS "Obłożenie w %"
FROM cap_per_month
LEFT JOIN sold_per_month ON sold_per_month.month = cap_per_month.month
ORDER BY "Miesiąc";