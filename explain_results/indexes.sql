
---q1 
---Raczej bezsonsowny index nie ma zazwyczaj potrzeby wiedzieć
CREATE INDEX idx_ticket_valid_used ON ticket(fk_screening_id) 
WHERE status IN ('used', 'valid'); --- specyficzny przypadek indexy po used i valid dla ticketów raczej nie poprawiają sprawności

CREATE INDEX idx_ticket_status ON ticket(status);  ---znacza część indeksów znajduje się w used lub unused (98%) więc indeksowanie w tym przypadku nie ma więszkego sensu 

---q2
---Kwerenda o charakterze statystycznynm 
CREATE INDEX idx_movie_version_version_id ON movie_version(fk_version_id);
CREATE INDEX idx_screening_movie_version_id ON screening(fk_movie_version_id);
---żadne z tych nie przynosi żadnych korzyści
---q3
---Wykonanie kwerendy zajmuje tylko 49ms
---q4
---Ten index również jest bezsensu, ponieważ musiałby być regularnie aktualizowany
CREATE INDEX idx_screening_recent_room ON screening(start_time, fk_room_id)
WHERE start_time >= (CURRENT_DATE - INTERVAL '1 year');


---q5 
---Średnia potrzeba optymalizacji, kwerenda o charakterze statystycznym 
CREATE INDEX idx_ticket_covering ON ticket(status, fk_ticket_type_id, fk_discount_id, _id);

--q22
---Kwerenda działa w7 9ms więc nie ma raczej potrzeby optymalizacji przez indeksy 