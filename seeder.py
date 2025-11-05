from db.connection import SessionLocal
from db.models import *
from faker import Faker 
from datetime import timedelta, datetime
import random

faker= Faker()


def seeder(seed_table, table_name, n):
    session = SessionLocal()
    try: 
        session.add_all(seed_table)
        session.add_all(seed_table)
        session.commit()
        print(f"Dodano {n} {table_name} do bazy danych!")
        print(f"Dodano {n} {table_name} do bazy danych!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally: 
        session.close()



def seed_version(): 
    languages=['polish', 'english', 'spanish', 'german'] 
    ver= ['2D', '3D', 'IMAX']
    versions=[] 
    for lang1 in languages: 
        for lang2 in languages:
            for v in ver:
                versions.append(Version(language=lang1, subtitles=lang2, format= v))
    seeder(versions, "version", len(versions))

def seed_license(n):
    licenses = [
        License(
            title=faker.sentence(nb_words=3),
            director=faker.name(),
            duration_minutes=faker.random_int(min=60, max=200),
            license_number=faker.random_int(min=1000000, max=9999999),
            start_date=faker.date_this_year(),
            end_date=faker.date_this_year(before_today=False, after_today=True),
            cost=faker.random_int(min=10000, max=100000)
        )
        for _ in range(n)
    ]
    seeder(licenses, "license", n)


def seed_movie_version(min_vers=1, max_vers=5):
    session= SessionLocal()
    movie_ids = [m[0] for m in session.query(Movie._id).all()]
    version_ids = [v[0] for v in session.query(Version._id).all()]
    movie_versions=[]
    if not movie_ids or not version_ids: 
        print("Brak filmów albo wersji do zaseedowania")
        return
    already_exists = set(session.query(MovieVersion.fk_movie_id,MovieVersion.fk_version_id).all())
    for mv in movie_ids:
        iter = random.randint(min_vers, max_vers)
        for vr in range(iter):
            pair=(mv, random.choice(version_ids))
            while pair in already_exists:
                pair = (mv, random.choice(version_ids))
            already_exists.add(pair)
            movie_versions.append(MovieVersion(fk_movie_id=pair[0], fk_version_id=pair[1]))
    seeder(movie_versions, "movie_version", len(movie_versions))


def seed_cinemas(n):
    session= SessionLocal()
    region_ids=[r[0] for r in session.query(Region._id).all()]
    cinemas=[Cinema(fk_region_id=random.choice(region_ids), city=faker.city_name(), street=faker.street_name(), building_number=random.randint(1, 30)) for _ in range(n)]
    seeder(cinemas, "cinema", n)


def seed_cinema_movie(n):
    session = SessionLocal()
    movie_ver_ids = [m[0] for m in session.query(MovieVersion._id).all()]
    cinema_ids = [c[0] for c in session.query(Cinema._id).all()]
    if not movie_ver_ids or not cinema_ids:
        print("Nie ma kin albo movie_version do seedowania")
        return
    already_exists = set(session.query(t_cinema_movie.c.fk_cinema_id,t_cinema_movie.c.fk_movie_version_id  ).all())
    new_records = []
    for _ in range(n):
        pair = (random.choice(cinema_ids), random.choice(movie_ver_ids))
        while pair in already_exists:
            pair = (random.choice(cinema_ids), random.choice(movie_ver_ids))
        already_exists.add(pair)
        new_records.append({'fk_cinema_id': pair[0], 'fk_movie_version_id': pair[1]})  
    try:
        session.execute(insert(t_cinema_movie), new_records)
        session.commit()
        print(f"Dodano {len(new_records)} rekordów do cinema_movie!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally:
        session.close()

def seed_room(n):
    session= SessionLocal()
    cinema_ids= [c[0] for c in session.query(Cinema._id).all()]
    already_exists = set(session.query(Room.fk_cinema_id, Room.number))
    rooms=[]
    for i in range(n):
        cid= random.choice(cinema_ids)
        pair=(cid, random.randint(1, 100000))
        while pair in already_exists:
            pair=(cid, random.randint(1, 100000))
        already_exists.add(pair)
        rooms.append(Room(fk_cinema_id=pair[0], number=pair[1]))
    seeder(rooms, "room", n)

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
                         start_time = faker.date_time_between(start_date=start_date_start, end_date=start_date_end).replace(second=0, microsecond=0),
                         end_time = None if random.random() < 0.1 else faker.date_time_between(start_date=start_date_end+timedelta(days=1), end_date=datetime.now()+timedelta(days=30)).replace(second=0, microsecond=0),
                         amount = faker.random_int(min=1, max=10)
                         )
                         for _ in range(n)), "special_offer", n)

def seed_seat(n):
    session = SessionLocal()
    room_ids = [x[0] for x in session.query(Room._id).all()]

    if len(room_ids) == 0 :
        print("Brak id w room")
        session.close()
        return
    
    seeder((Seat(fk_room_id = random.choice(room_ids),
                 seat_num = i
                 )
                 for i in range(n)), "seat", n)
    session.close()

def seed_ticket(n):
    session = SessionLocal()
    ticket_type_ids = [x[0] for x in session.query(TicketType._id).all()]
    seat_ids = [x[0] for x in session.query(Seat._id).all()]
    screening_ids = [x[0] for x in session.query(Screening._id).all()]
    discount_ids = [x[0] for x in session.query(Discount._id).all()]
    payment_ids = [x[0] for x in session.query(Payment._id).all()]

    statuses = ['used', 'valid', 'reserved', 'payment_pending', 'free']

    if len(ticket_type_ids) == 0 :
        print("Brak id w ticket_type")
        session.close()
        return
    
    if len(seat_ids) == 0 :
        print("Brak id w seat")
        session.close()
        return
    
    if len(screening_ids) == 0 :
        print("Brak id w screening")
        session.close()
        return
    
    if len(discount_ids) == 0 :
        print("Brak id w discount")
        session.close()
        return
    
    if len(payment_ids) == 0 :
        print("Brak id w payment")
        session.close()
        return

    seeder((Ticket(fk_ticket_type_id = random.choice(ticket_type_ids),
                   fk_seat_id = random.choice(seat_ids),
                   fk_screening_id = random.choice(screening_ids),
                   fk_discount_id = None if random.random() < 0.5 else random.choice(discount_ids),
                   fk_payment_id = None if random.random() < 0.25 else random.choice(payment_ids),
                   qr_code = faker.word(),
                   status = random.choice(statuses),
                   price = 0 # TO-DO: pętla uzupełniająca to realnie (tak samo amount w payment)
                   )
                   for _ in range(n)), "ticket", n)
    session.close()


# TABELA POSREDNIA - NIE MODEL ORM - TROCHE INACZEJ
def seed_ticket_special_offer(n):
    session = SessionLocal()
    ticket_ids = [x[0] for x in session.query(Ticket._id).all()]
    special_offer_ids = [x[0] for x in session.query(SpecialOffer._id).all()]

    if len(ticket_ids) == 0 :
        print("Brak id w ticket")
        session.close()
        return
    
    if len(special_offer_ids) == 0 :
        print("Brak id w special_offer")
        session.close()
        return

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


def seed_ticket_with_realistic_price():
    session = SessionLocal()
    tickets = session.query(Ticket).all()

    try: 
        for t in tickets:
            discount_obj = session.query(Discount).filter(Discount._id == t.fk_discount_id).first()
            dsc = discount_obj.percentage if discount_obj else None
            type_price = session.query(TicketType).filter(TicketType._id == t.fk_ticket_type_id).first().price
            special_offers = [s.amount for s in t.fk_special_offer]

            new_price_base = type_price

            for i in range(len(special_offers)):
                if new_price_base > 0:
                    new_price_base -= special_offers[i]

            if dsc is not None:
                new_price = new_price_base - (dsc/100)*new_price_base

            t.price = new_price
        session.commit()
        print("Zmieniono ceny biletów na realistyczne")
    except Exception as e:
        session.rollback()
        print("Błąd podczas zmiany cen biletów:", e)
    finally: 
        session.close()



if __name__ == "__main__":
    print("Zaczynam seedowanie")


