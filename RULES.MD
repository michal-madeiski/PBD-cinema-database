# ZASADY KODU:
1. WSZYSTKIE nazwy z małej (tabeli, atrybutów, ograniczeń, enumów), bo postgres i tak zamienia wszystko potem na małe litery i w skryptach będzie problem i bałagan a tak to wszędzie wszystko Z MAŁYCH (snake_case).  
   
2. Spójna konwencja typów: daty (bez czasu) to DATE; data+czas to TIMESTAMP(0) - 0 oznacza bez sekund; tekstowe to VARCHAR(50), chyba że coś może być dłuższe np. qr code to wtedy więcej; liczbowe to int a ceny itp to NUMERIC(10, 2), chyba że coś ma konkertny zakres np. procenty to NUMERIC(4, 2).  
   
3. Nazwy constraintów dla fk: c_fk_jakas_nazwa - aby nie powtarzać nazwy tego fk. Przykładowo:  
   fk_ticket_type_id INT NOT NULL,  
   CONSTRAINT c_fk_ticket_type_id  
  
4. Przyjmijmy, że najbardziej akutalna wersja diagramu jest na DRAWIO, a na gita damy dopiero jak skończymy ten etap, żeby nie commitować co chwilę zmiany png.