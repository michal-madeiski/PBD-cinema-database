from db.connection import SessionLocal
from db.models import *
from faker import Faker 
from datetime import timedelta, datetime, date
import random
from sqlalchemy import select, func
from decimal import Decimal

faker= Faker("pl_PL")

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

def seeder_region(n):
    session = SessionLocal()
    existing_names = set(t.name for t in session.query(Region).all())
    names = set()
    for _ in range(n):
        name = faker.administrative_unit()
        if name not in names and name not in existing_names:
            names.add(name)
    session.close()     
    seeder([Region(name = name) for name in names], "region", len(names))

def seeder_product(n):
    session = SessionLocal()
    names = set()
    barcodes = set()
    products = []
    existing_names = set(t.name for t in session.query(Product).all())
    existing_barcodes = set(t.barcode for t in session.query(Product).filter(Product.barcode.isnot(None)).all())
    for _ in range(n):
        name = faker.word()
        barcode = faker.ean13() if random.random() > 0.2 else None
        price = faker.pyfloat(min_value=2, max_value=100, right_digits=2, positive=True)
        is_available = faker.boolean()

        if name in names or name in existing_names:
            continue

        if barcode is not None and (barcode in barcodes or barcode in existing_barcodes):
            continue
            
        names.add(name)

        if barcode is not None:
            barcodes.add(barcode)
        products.append(Product(name = name, barcode = barcode, price = price, is_available = is_available))

    session.close()
    seeder(products, "product", len(products))

def seeder_screening(n):
    session = SessionLocal()
    screenings = []
    room_ids = [x._id for x in session.query(Room).all()]
    movie_version_ids = [x._id for x in session.query(MovieVersion).all()]
    movie_version_data = session.query(MovieVersion._id, Movie.duration_minutes ,License.start_date, License.end_date).join(Movie, Movie._id == MovieVersion.fk_movie_id).join(License, License._id == Movie._id).order_by(MovieVersion._id).all()

    movie_version_data = {
        mv_id: (duration, start_date, end_date)
        for mv_id, duration, start_date, end_date in movie_version_data
    }

    if(len(room_ids) == 0):
        print("Brak danych w tabeli Room")
        session.close()
        return
    if(len(movie_version_ids) == 0):
        print("Brak danych w tabeli MovieVersion")
        session.close()
        return
    
    for _ in range(n):
        movie_version_id = random.choice(list(movie_version_data.keys()))
        fk_room_id = random.choice(room_ids)
        start_time = faker.date_time_between(start_date = movie_version_data[movie_version_id][1], end_date = movie_version_data[movie_version_id][2])
        start_time = start_time.replace(second=0, microsecond=0)
        duration = movie_version_data[movie_version_id][0]
        end_time = start_time + timedelta(minutes = duration + 40)
        screenings.append(Screening(fk_room_id = fk_room_id, fk_movie_version_id = movie_version_id, start_time = start_time, end_time = end_time))
    session.close()
    seeder(screenings, "screening", len(screenings))

def seeder_product_sale(n):
    product_sales = []
    session = SessionLocal()
    products = session.query(Product).all()
    payment_ids = [t._id for t in session.query(Payment).all()]
    cinema_ids = [t._id for t in session.query(Cinema).all()]

    if(len(products) == 0):
        print("Brak danych w tabeli Product")
        session.close()
        return
    if(len(payment_ids) == 0):
        print("Brak danych w tabeli Payment")
        session.close()
        return
    if(len(cinema_ids) == 0):
        print("Brak danych w tabeli Cinema")
        session.close()
        return
    
    for _ in range(n):
        product = random.choice(products)
        fk_product_id = product._id
        fk_payment_id = random.choice(payment_ids)
        fk_cinema_id = random.choice(cinema_ids)
        price = product.price
        product_sales.append(ProductSale(fk_product_id = fk_product_id, fk_payment_id = fk_payment_id, fk_cinema_id = fk_cinema_id, price = price))
    session.close()
    seeder(product_sales, "product_sale", len(product_sales))

def seeder_payment(n):
    payments = []
    session = SessionLocal()
    client_ids = [t._id for t in session.query(Client).all()]

    if(len(client_ids) == 0):
        print("Brak danych w tabeli Client")
        session.close()
        return
    
    for _ in range(n):
        fk_client_id = random.choice(client_ids) if random.random() > 0.2 else None
        payment_type = random.choice(['cash', 'card', 'blik', 'online', 'voucher'])
        time_of_payment = faker.date_time_between(start_date=datetime(1970, 1, 1), end_date=datetime.now())
        amount = Decimal("0.00")
        payments.append(Payment(fk_client_id = fk_client_id, type = payment_type, time_of_payment = time_of_payment, amount = amount))
    session.close()
    seeder(payments, "payment", len(payments))

def calculate_payments():
    session = SessionLocal()
    ticket_prices = (
        session.query(Payment._id, func.sum(Ticket.price))
        .outerjoin(Ticket, Ticket.fk_payment_id == Payment._id)
        .group_by(Payment._id)
        .order_by(Payment._id)
        .all())

    product_sale_prices = (
        session.query(Payment._id, func.sum(ProductSale.price))
        .outerjoin(ProductSale, ProductSale.fk_payment_id == Payment._id)
        .group_by(Payment._id)
        .order_by(Payment._id)
        .all())
    
    ticket_dict = dict(ticket_prices)
    product_sale_dict = dict(product_sale_prices)

    totals = {          
        payment_id: (ticket_dict.get(payment_id) or Decimal("0.00")) + (product_sale_dict.get(payment_id) or Decimal("0.00"))
        if (ticket_dict.get(payment_id) is not None or product_sale_dict.get(payment_id) is not None)
        else None
        for payment_id in ticket_dict
    }

    updates = [{"_id": payment_id, "amount": totals[payment_id]} for payment_id in totals]

    session.bulk_update_mappings(Payment, updates)
    session.query(Payment).filter(Payment.amount.is_(None)).delete(synchronize_session=False)
    session.commit()
    session.close()
    print("Zliczono i usunięto paymenty")

def seeder_term(n):
    terms = []
    session = SessionLocal()
    region_ids = [t._id for t in session.query(Region).all()]
    regional_manager_ids = [t._id for t in session.query(RegionalManager).all()]

    if(len(region_ids) == 0):
        print("Brak danych w tabeli Region")
        session.close()
        return
    
    if(len(regional_manager_ids) == 0):
        print("Brak danych w tabeli RegionalManager")
        session.close()
        return
    
    last_start_dates = session.query(Region._id, func.min(Term.start_date)).outerjoin(Term, Term.fk_region_id == Region._id).group_by(Region._id).order_by(Region._id).all()
    last_start_dates = dict(last_start_dates)
    
    for _ in range(n):
        region = random.choice(list(last_start_dates.keys()))
        last_start_date = last_start_dates[region]
        fk_region_id = region
        fk_manager_id = random.choice(regional_manager_ids)
        if last_start_date == date(1970, 1, 1):
            continue
        if last_start_date is None:
            end_date = date.today()
        else:
            end_date = last_start_date - timedelta(days=1)
        days = random.randint(0, 1825)
        start_date = max(end_date - timedelta(days=days), date(1970, 1, 1))
        last_start_dates[fk_region_id] = start_date
        terms.append(Term(fk_region_id = fk_region_id, fk_manager_id = fk_manager_id, start_date = start_date, end_date = end_date))

    session.close()
    seeder(terms, "term", len(terms))

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
    session= SessionLocal()
    already_exists=set(l[0] for l in session.query(License.license_number).all())
    licenses=[]
    for i in range(n):
        number= faker.random_int(min=1000, max=99999999)
        while number in already_exists:
            number= faker.random_int(min=1000, max=99999999)
        already_exists.add(number)
        lic= License(
            title=faker.sentence(nb_words=2, variable_nb_words=True),
            director=faker.name(),
            duration_minutes=faker.random_int(min=60, max=200),
            license_number=number,
            start_date=faker.date_this_year(),
            end_date=faker.date_this_year(before_today=False, after_today=True),
            cost=faker.random_int(min=10000, max=100000)
        )
        licenses.append(lic)

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
    cinemas=[Cinema(fk_region_id=random.choice(region_ids), city=faker.city(), street=faker.street_name(), building_number=random.randint(1, 30)) for _ in range(n)]
    seeder(cinemas, "cinema", n)


def seed_cinema_movie(n):
    session = SessionLocal()
    movie_ver_ids = [m[0] for m in session.query(MovieVersion._id).all()]
    cinema_ids = [c[0] for c in session.query(Cinema._id).all()]
    if not movie_ver_ids or not cinema_ids:
        print("Nie ma kin albo movie_version do seedowania")
        return
    already_exists = set(session.query(t_cinema_movie_version.c.fk_cinema_id,t_cinema_movie_version.c.fk_movie_version_id  ).all())
    new_records = []
    for _ in range(n):
        pair = (random.choice(cinema_ids), random.choice(movie_ver_ids))
        while pair in already_exists:
            pair = (random.choice(cinema_ids), random.choice(movie_ver_ids))
        already_exists.add(pair)
        new_records.append({'fk_cinema_id': pair[0], 'fk_movie_version_id': pair[1]})  
    try:
        session.execute(t_cinema_movie_version.insert(), new_records)
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
                 seat_num = i+1
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
                   qr_code = faker.ean13(),
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
    stmt = select(t_ticket_special_offer.c.fk_ticket_id, t_ticket_special_offer.c.fk_special_offer_id)
    ticket_special_offers = session.execute(stmt).fetchall()
    existed_pairs = {(r.fk_ticket_id, r.fk_special_offer_id) for r in ticket_special_offers}

    pairs = set()
    pair= ((random.choice(ticket_ids), random.choice(special_offer_ids)))
    while len(pairs) < n:
        while pair in pairs or pair in existed_pairs:
            pair= ((random.choice(ticket_ids), random.choice(special_offer_ids)))
        pairs.add(pair)

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
        
def seed_users_base(ModelClass, n):
    session = SessionLocal()
    objects = []

    used_emails = {e for (e,) in session.query(User.email).all()}
    used_usernames = {u for (u,) in session.query(User.username).all()}

    for _ in range(n):

   
        email = faker.email()

        while(email in used_emails):
            # used_emails.add(email)
            email += "x"
        used_emails.add(email)
            
        username = faker.user_name()
        while(username in used_usernames):
            # used_usernames.add(username)
            username += "x"
        used_usernames.add(username)
            


        account_create_date = faker.date_between(start_date='-5y', end_date='today')
        if random.random() < 0.9:
            now_minus_5h = datetime.now() - timedelta(hours=5)
            last_login_time = faker.date_time_between(start_date=account_create_date, end_date=now_minus_5h)
        else:
            last_login_time = None
            

        data = {
            "name": faker.first_name(),
            "surname": faker.last_name(),
            "birthdate": faker.date_of_birth(minimum_age=10, maximum_age=60),
            "username": username,
            "email": email,
            "password": "$2b$12$hashed_password_example",
            "account_create_date": account_create_date,
            "last_login_time": last_login_time
        }

        obj = ModelClass(**data)
        objects.append(obj)

    try:
        session.add_all(objects)
        session.commit()
        print(f"Dodano {n} rekordów do {ModelClass.__name__}!")
        return objects
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally:
        session.close()


def seed_workers_base(ModelClass, n):
    session = SessionLocal()
    objects = []

    used_emails = {e for (e,) in session.query(User.email).all()}
    used_usernames = {u for (u,) in session.query(User.username).all()}
    used_pesels = {u for (u,) in session.query(Worker.pesel_number).all()}
    used_bank_account_numbers = {u for (u,) in session.query(Worker.bank_account_number).all()}

    for _ in range(n):

        while True:
            email = faker.email()
            if email not in used_emails:
                used_emails.add(email)
                break

        while True:
            username = faker.user_name()
            if username not in used_usernames:
                used_usernames.add(username)
                break
        
        while True:
            pesel = faker.pesel()
            if pesel not in used_pesels:
                used_pesels.add(pesel)
                break

        while True:
            bank_acc = ''.join([str(random.randint(0, 9)) for _ in range(26)])
            if bank_acc not in used_bank_account_numbers:
                used_bank_account_numbers.add(bank_acc)
                break

        account_create_date = faker.date_between(start_date='-5y', end_date='today')
        
        if random.random() < 0.9:
            now_minus_5h = datetime.now() - timedelta(hours=5)
            last_login_time = faker.date_time_between(start_date=account_create_date, end_date=now_minus_5h)
        else:
            last_login_time = None

        data = {
            "name": faker.first_name(),
            "surname": faker.last_name(),
            "birthdate": faker.date_of_birth(minimum_age=18, maximum_age=60),
            "username": username,
            "email": email,
            "password": "$2b$12$hashed_password_example",
            "account_create_date": account_create_date,
            "last_login_time": last_login_time,
            "pesel_number":pesel,
            "bank_account_number": bank_acc,
            "salary_month": random.randint(3000, 7000)
        }

        obj = ModelClass(**data)
        objects.append(obj)

    try:
        session.add_all(objects)
        session.commit()
        print(f"Dodano {n} rekordów do {ModelClass.__name__}!")
        return objects
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally:
        session.close()

def seed_client(n):
    return seed_users_base(Client, n)

def seed_regional_manager(n):
    return seed_users_base(RegionalManager, n)
    
def seed_supervisor(n):
   return seed_workers_base(Supervisor, n)

def seed_service(n):
   return seed_workers_base(Service, n)



def seed_employment(n):
    session = SessionLocal()

    worker_ids = [w[0] for w in session.query(Worker._id).all()]
    cinema_ids = [c[0] for c in session.query(Cinema._id).all()]

    if not worker_ids or not cinema_ids:
        print("Brakuje workerów lub kin — seeduj je najpierw!")
        session.close()
        return

    employments = []

    for _ in range(n):
        worker_id = random.choice(worker_ids)
        cinema_id = random.choice(cinema_ids)


        start_date = faker.date_between(start_date='-5y', end_date='-1y')


        if random.random() < 0.3:
            months = random.randint(6, 24)
            end_date = start_date + timedelta(days=30 * months)
            if end_date > datetime.today().date():
                end_date = datetime.today().date()
        else:
            end_date = None
            
        emp = Employment(
            fk_worker_id=worker_id,
            fk_cinema_id=cinema_id,
            start_date=start_date,
            end_date=end_date
        )
        employments.append(emp)

    try:
        session.add_all(employments)
        session.commit()
        print(f"Dodano {n} rekordów do Employment!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally:
        session.close()

def seed_shift(n):
    session = SessionLocal()

    worker_ids = [w[0] for w in session.query(Worker._id).all()]
    if not worker_ids:
        print("Brak workerów — seeduj workerów najpierw!")
        session.close()
        return

    SHIFT_TYPES = ['cashier', 'usher', 'cleaning', 'projection', 'technical_support']

    shifts = []

    for i in range(n):
        worker_id = random.choice(worker_ids)

        start = faker.date_time_between(start_date='-60d', end_date='now')
        end = start + timedelta(hours=random.randint(6, 10))
        shift_type = random.choice(SHIFT_TYPES)

        shift = Shift(
            fk_worker_id=worker_id,
            start_time=start,
            end_time=end,
            type=shift_type
        )
        shifts.append(shift)

        if (i+1) % 100_000 == 0:
            print(f"{i}\n")

    try:
        session.add_all(shifts)
        session.commit()
        print(f"Dodano {n} rekordów do Shift!")
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


    movie_and_license_count=250
    cinema_movie=20
    min_versions=1
    max_versions=5
    cinema_count=20
    room_counts= cinema_count*5
    SERVICES = 200
    SUPERVISORS = 50
    CLIENTS = 1_000
    REGIONAL_MANAGERS = 10
    SHIFTS = 4_000
    EMPLOYMENTS = 400
    region_count = 100
    product_count = 1000
    screening_count = 3_000
    product_sale_count = 1_000
    payment_count = 2_000
    term_count = 200
    TICKET_COUNT = 5_000
    SPECIAL_OFFER_COUNT = 200
    SEAT_COUNT = room_counts*50
    TICKET_SPECIAL_OFFER_COUNT = 2_500

    #seedery, które nie potrzebują innych tabel
    seeder_region(region_count)
    seeder_product(product_count)
    seed_client(CLIENTS)
    seeder_payment(500)

    seed_license(movie_and_license_count)
    seed_version()
    seed_movie_version(min_versions, max_versions)
    #wymaga regionu
    seed_cinemas(cinema_count)
    seed_cinema_movie(cinema_movie)
    seed_room(room_counts)

   
    seed_service(SERVICES)
    seed_regional_manager(REGIONAL_MANAGERS)
    seed_shift(SHIFTS//5)
    seed_shift(SHIFTS//5)
    seed_shift(SHIFTS//5)
    seed_shift(SHIFTS//5)
    seed_shift(SHIFTS//5)


    #WYMAGA CINEMA 
    seed_employment(EMPLOYMENTS)


    # seedery, które potrzebują innych tabel
    seeder_screening(screening_count//5) # room, movie_version
    seeder_screening(screening_count//5)
    seeder_screening(screening_count//5)
    seeder_screening(screening_count//5)
    seeder_screening(screening_count//5)


    seeder_product_sale(product_sale_count//10) #product, payment, cinema
    seeder_product_sale(product_sale_count//10)
    seeder_product_sale(product_sale_count//10)
    seeder_product_sale(product_sale_count//10)
    seeder_product_sale(product_sale_count//10)

    seeder_term(term_count) # region, regional_manager


    

    seed_special_offer(SPECIAL_OFFER_COUNT)
    seed_discount() 
    seed_ticket_type()
    seed_seat(SEAT_COUNT) #room 
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    seed_ticket(TICKET_COUNT//20)
    
     #ticket_type, discount, payment, seat, screening
    seed_ticket_special_offer(TICKET_SPECIAL_OFFER_COUNT//10)
    seed_ticket_special_offer(TICKET_SPECIAL_OFFER_COUNT//10)
    seed_ticket_special_offer(TICKET_SPECIAL_OFFER_COUNT//10)
    seed_ticket_special_offer(TICKET_SPECIAL_OFFER_COUNT//10)
    seed_ticket_special_offer(TICKET_SPECIAL_OFFER_COUNT//10) #ticket, special_offer
    seed_ticket_with_realistic_price()

    calculate_payments()