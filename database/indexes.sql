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