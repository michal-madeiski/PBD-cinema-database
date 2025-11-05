# Seeder.py - instrukcja obsługi:

### (pamiętajcie o edycji pliku example.env - nazwa usera i hasło)

---

1. główna funkcja seedująca to "seeder":
   
   ```python 
   def seeder(seed_table, table_name, n):
    session = SessionLocal()
    try: 
        session.add_all(seed_table)
        session.commit()
        print(f"Dodano {n} {table_name} do bazy danych!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally: 
        session.close()
    ```

2. każda tabela ma osobną funkcję seedującą np.:
   ```python
   def seed_seat(n):
    session = SessionLocal()
    room_ids = [x.id for x in session.query(Room._id).all()]
    seeder((Seat(fk_room_id = random.choice(room_ids),
                 seat_num = i
                 )
                 for i in range(n)), "seat", n)
    session.close()
    ```
3. jak pisać te funkcje?
- gdy potrzeba fk trzeba otworzyć sesje (na koniec funkcji trzeba zamknąć) i pobrać id przez query - bo kolejność dodawania do bazy będzie taka, że te id już będą istnieć - tak jak w seed_seat powyżej
  
 - jeśli tabela jest na tyle mała, że można to zrobić ręcznie to chyba lepiej ręcznie np.: 
  ```python
  def seed_discount():
    seeder((Discount(name='student', percentage=21),
            Discount(name='school', percentage=15),
            Discount(name='senior', percentage=12),
            Discount(name='military', percentage=10)
            ),
            "discount", 4)
  ```
  
  - orm odwzorowuje modele jako obiekty, ale nie tabele pośrednie zawierające same fk (u nas są takie dwie: ticket_special_offer i cinema_movie), wtedy trzeba zrobić trochę inaczej: 
  ```python
  def seed_ticket_special_offer(n):
    session = SessionLocal()
    ticket_ids = [x.id for x in session.query(Ticket._id).all()]
    special_offer_ids = [x.id for x in session.query(SpecialOffer._id).all()]

    # set bo para jako klucz główny czyli ma być bez powtórzeń
    pairs = set()

    while len(pairs) < n:
        pairs.add((random.choice(ticket_ids), random.choice(special_offer_ids)))
    

    data = [{"fk_ticket_id": t, "fk_special_offer_id": s} for t, s in pairs]

    try: 
        session.execute(t_ticket_special_offer.insert(), data)
        session.commit()
        print(f"Dodano {len(data)} ticket_special_offer do bazy danych!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally: 
        session.close()
  ```
