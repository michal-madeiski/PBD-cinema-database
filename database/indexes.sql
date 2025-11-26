--q_01 
--specyficzny przypadek indexy po used i valid dla ticketów raczej nie poprawiają sprawności
--znacza część indeksów znajduje się w used lub not_used (98%) więc indeksowanie w tym przypadku nie ma więszkego sensu 
CREATE INDEX idx_ticket_valid_used_fk_screening_id ON ticket(fk_screening_id) WHERE status IN ('used', 'valid'); 
CREATE INDEX idx_ticket_status ON ticket(status);

--q_02
--kwerenda o charakterze statystycznynm, żadne z poniższych nie przynosi korzyści
CREATE INDEX idx_movie_version_fk_version_id ON movie_version(fk_version_id);
CREATE INDEX idx_screening_fk_movie_version_id ON screening(fk_movie_version_id); --używane w q_12, q_13

--q_03
--wykonanie kwerendy zajmuje tylko 49ms

--q_04
--ten index również jest bezsensu, ponieważ musiałby być regularnie aktualizowany
--CREATE INDEX idx_screening_recent_room_id ON screening(start_time, fk_room_id) WHERE start_time >= (CURRENT_DATE - INTERVAL '1 year');

--q_05 
--średnia potrzeba optymalizacji, kwerenda o charakterze statystycznym 
CREATE INDEX idx_ticket_covering ON ticket(status, fk_ticket_type_id, fk_discount_id, _id);

--q_06
--silnik postgresql zawsze przejdzie po obu tabelach dokładnie 1 raz

--q_07
--silnik postgresql zawsze przejdzie po obu tabelach dokładnie 1 raz

--q_08
--tabele cinema i room są bardzo małe, w filter screening i tak bierze około 98% rekordów, więc index prawie nic tu nie da, a nawet spowolni zapytanie

--q_09
CREATE INDEX idx_screening_start_time_fk_room_id ON screening(start_time, fk_room_id);
CREATE INDEX idx_ticket_fk_screening_id ON ticket(fk_screening_id); --używane w q_21

--q_10
--silnik postgresql i tak musi przejść po 98% screeningów, więc nie użyje indexów dla ticketów

--q_11
CREATE INDEX idx_product_sale_fk_payment_id ON product_sale(fk_payment_id);
CREATE INDEX idx_ticket_fk_payment_id ON ticket(fk_payment_id); --używane w q_23

--q_12
--korzysta z indeksu dla q_02

--q_13
--Korzysta z indeksu dla q_02.

--q_14
CREATE INDEX idx_shift_type ON shift(type);

--q_15
CREATE INDEX idx_worker_user_id ON worker(_id);
CREATE INDEX idx_employment_fk_worker_id ON employment(fk_worker_id);

--q_16
--nawet z indeksami postgresql nie korzystał z nich, ponieważ dla dużych danych pełny skan + parallel sort były tańsze niż użycie indeksu

--q_17
CREATE INDEX idx_ticket_used_fk_screening_id ON ticket(fk_screening_id) WHERE status = 'used';
CREATE INDEX idx_screening_start_time_id ON screening(start_time, _id);

--q_18
CREATE INDEX idx_ticket_price_zero ON ticket(price) WHERE price = 0;

--q_19
CREATE INDEX idx_shift_worker_time_covering ON shift(fk_worker_id, start_time, end_time);

--q_20
--kwerenda trwa milisekundy

--q_21
--korzysta z indeksu dla q_01
CREATE INDEX idx_seat_room_id ON seat(fk_room_id);

--q22
--kwerenda działa w 9ms więc nie ma potrzeby optymalizacji przez indeksy 

--q_23
--korzysta z indeksu dla q_11
CREATE INDEX idx_payment_fk_client_id ON payment(fk_client_id);

--q_24
CREATE INDEX idx_cinema_city ON cinema(city);

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    indexname LIKE 'idx%'
ORDER BY
    schemaname,
    tablename;