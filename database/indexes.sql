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