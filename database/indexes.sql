<<<<<<< HEAD
-- q_16
-- Po dodaniu indeksów PostgreSQL nadal korzystał z pełnego skanowania i równoległego sortowania,
-- ponieważ dla dużych danych pełny skan + parallel sort były tańsze niż użycie indeksu.

-- q_17
CREATE INDEX idx_ticket_used_fk_screening ON ticket (fk_screening_id) WHERE status = 'used';
CREATE INDEX idx_screening_start_time_id ON screening (start_time, _id);

-- q_18
CREATE INDEX idx_ticket_price_zero ON ticket (price) WHERE price = 0;

-- q_19
CREATE INDEX idx_shift_worker_time_covering ON shift(fk_worker_id, start_time, end_time);

-- q_20
-- Nie trzeba indeksów bo już zoptymalizowane przez postgresa (milisekunda na obliczenie)

-- q_24
CREATE INDEX idx_cinema_city_lower ON cinema (LOWER(city));

--q_11
CREATE INDEX idx_product_sale_fk_payment ON product_sale(fk_payment_id);
CREATE INDEX idx_ticket_fk_payment ON ticket(fk_payment_id);

--q_12
CREATE INDEX idx_screening_fk_movie_version ON screening(fk_movie_version_id);

--q_13
--Korzysta z indeksu dla q_12.

--q_14
CREATE INDEX idx_shift_type ON shift(type);

--q_15
CREATE INDEX idx_worker_user ON worker(_id);
CREATE INDEX idx_employment_fk_worker ON employment(fk_worker_id);

--q_21
CREATE INDEX idx_seat_room ON seat(fk_room_id);
CREATE INDEX idx_ticket_screening_status ON ticket(fk_screening_id);
=======
-- q_06
-- Nie opłaca się robić żadnego indexu, ponieważ silnik PostgreSQL zawsze przejdzie po obu tabelach dokładnie 1 raz

-- q_07
-- Nie opłaca się robić żadnego indexu, ponieważ silnik PostgreSQL zawsze przejdzie po obu tabelach dokładnie 1 raz

-- q_08
-- Nie opłaca się robić żadnego indexu, ponieważ tabela cinema i room są bardzo małe, w filter screening i tak bierze około 98% rekordów, więc index prawie nic tu nie da, a nawet spowolni zapytanie.

-- q_09
CREATE INDEX idx_screening_start_time_fk_room_id ON screening(start_time, fk_room_id);
CREATE INDEX idx_ticket_fk_screening_id ON ticket(fk_screening_id);

-- q_10
-- Nie opłaca się robić żadnego indexu, ponieważ silnik PostgreSQL i tak musi przejść po 98% screeningów, więc nie użyje indexów dla ticketów.

-- q_23
CREATE INDEX idx_payment_fk_client_id ON payment(fk_client_id);
CREATE INDEX idx_ticket_fk_payment_id ON ticket(fk_payment_id);
>>>>>>> origin/marciniak
