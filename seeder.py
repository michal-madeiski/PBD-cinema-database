from db.connection import SessionLocal
from db.models import *
from faker import Faker 
from datetime import timedelta, datetime
import random

faker= Faker()

# KOD KAMIONKI:
# def seed_movies(n):
#     session = SessionLocal()
#     try: 
#         movies= (Movie(title=faker.word(), director=faker.name(), duration_minutes=faker.random_int(min=60, max=200)) for i in range(n))
#         session.add_all(movies)
#         session.commit()
#         print(f"Dodano {n} filmów do bazy danych!")
#     except Exception as e:
#         session.rollback()
#         print("Błąd podczas seedowania:", e)
#     finally: 
#         session.close()


#główna funkcja:
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


#funkcje do pojedynczych tabel:
def seed_discount():
    seeder((Discount(name='student', percentage=21),
            Discount(name='school', percentage=15),
            Discount(name='senior', percentage=12),
            Discount(name='military', percentage=10)
            ),
            "discount", 4)

def seed_ticket_type():
    seeder((TicketType(name='standard', price=30),
            TicketType(name='reduced', price=25)
            ),
            "ticket_type", 2)

def seed_special_offer(n):
    start_date_start = datetime.now()-timedelta(days=1000)
    start_date_end = start_date_start+timedelta(days=900)

    seeder((SpecialOffer(name = faker.word(),
                         start_time = faker.date_time_between(start_date=start_date_start, end_date=start_date_end),
                         end_time = faker.date_time_between(start_date=start_date_end+timedelta(days=1), end_date=datetime.now()+timedelta(days=30)),
                         amount = faker.random_int(min=1, max=10)
                         )
                         for _ in range(n)), "special_offer", n)

def seed_seat(n):
    session = SessionLocal()
    room_ids = [x.id for x in session.query(Room._id).all()]
    seeder((Seat(fk_room_id = random.choice(room_ids),
                 seat_num = i
                 )
                 for i in range(n)), "seat", n)
    session.close()

def seed_ticket(n):
    session = SessionLocal()
    ticket_type_ids = [x.id for x in session.query(TicketType._id).all()]
    seat_ids = [x.id for x in session.query(Seat._id).all()]
    screening_ids = [x.id for x in session.query(Screening._id).all()]
    discount_ids = [x.id for x in session.query(Discount._id).all()]
    payment_ids = [x.id for x in session.query(Payment._id).all()]

    statuses = ['used', 'valid', 'reserved', 'payment_pending', 'free']

    seeder((Ticket(fk_ticket_type_id = random.choice(ticket_type_ids),
                   fk_seat_id = random.choice(seat_ids),
                   fk_screening_id = random.choice(screening_ids),
                   fk_discount_id = random.choice(discount_ids),
                   fk_payment_id = random.choice(payment_ids),
                   qr_code = faker.word(),
                   status = random.choice(statuses),
                   price = 0 # TO-DO: pętla uzupełniająca to realnie (tak samo amount w payment)
                   )
                   for _ in range(n)), "ticket", n)
    session.close()


# TABELA POSREDNIA - NIE MODEL ORM - TROCHE INACZEJ
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


if __name__ == "__main__":
    print("Zaczynam seedowanie")
    #seed_discount()
    #seed_ticket_type()
    #seed_special_offer(10_000)
    #seed_seat(100_000)
    #seed_ticket(1_000_000)
    #seed_ticket_special_offer(250_000)