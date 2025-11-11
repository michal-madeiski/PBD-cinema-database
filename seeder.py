from db.connection import SessionLocal
from db.models import *
from faker import Faker 
from datetime import timedelta, datetime, date, timezone
import random
from sqlalchemy import select, func, update, exists
from decimal import Decimal
from bisect import bisect_right
from collections import defaultdict



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
    movie_version_data = session.query(MovieVersion._id, Movie.duration_minutes ,License.start_date, License.end_date).join(Movie, Movie._id == MovieVersion.fk_movie_id).join(License, License._id == MovieVersion.fk_movie_id).order_by(MovieVersion._id).all()
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
        end = datetime.now() - timedelta(hours=5)
        time_of_payment = faker.date_time_between_dates(datetime_start=datetime(2015, 1, 1), datetime_end=end, tzinfo=None)
        amount = Decimal("0.00")
        payments.append(Payment(fk_client_id = fk_client_id, type = payment_type, time_of_payment = time_of_payment, amount = amount))
    session.close()
    seeder(payments, "payment", len(payments))

def calculate_payments(batch_size=200_000):
    session = SessionLocal()
    try:
        lo, hi = session.query(func.min(Payment._id), func.max(Payment._id)).one()
        if lo is None:
            print("Brak rekordów w payment.")
            return

        cur = lo
        batch_no = 0
        while cur <= hi:
            end = min(cur + batch_size - 1, hi)
            batch_no += 1

            # --- AGREGACJE W DB – tylko dla payment_id w przedziale ---
            t_subq = (
                session.query(
                    Ticket.fk_payment_id.label("pid"),
                    func.sum(Ticket.price).label("sum_t"),
                )
                .filter(Ticket.fk_payment_id.between(cur, end))
                .group_by(Ticket.fk_payment_id)
                .subquery()
            )

            p_subq = (
                session.query(
                    ProductSale.fk_payment_id.label("pid"),
                    func.sum(ProductSale.price).label("sum_p"),
                )
                .filter(ProductSale.fk_payment_id.between(cur, end))
                .group_by(ProductSale.fk_payment_id)
                .subquery()
            )

            agg = (
                session.query(
                    func.coalesce(t_subq.c.pid, p_subq.c.pid).label("pid"),
                    func.coalesce(t_subq.c.sum_t, 0).label("sum_t"),
                    func.coalesce(p_subq.c.sum_p, 0).label("sum_p"),
                )
                .select_from(t_subq.outerjoin(p_subq, t_subq.c.pid == p_subq.c.pid))
                .subquery("agg")
            )

            # --- UPDATE payment.amount = sum_t + sum_p dla batcha ---
            stmt_upd = (
                update(Payment)
                .where(Payment._id == agg.c.pid)
                .where(Payment._id.between(cur, end))
                .values(amount=agg.c.sum_t + agg.c.sum_p)
            )
            session.execute(stmt_upd)

            # --- DELETE paymentów bez powiązań (tylko w batchu) ---
            ticket_exists = exists().where(Ticket.fk_payment_id == Payment._id)
            product_exists = exists().where(ProductSale.fk_payment_id == Payment._id)

            (session.query(Payment)
                .filter(Payment._id.between(cur, end))
                .filter(~ticket_exists, ~product_exists)
                .delete(synchronize_session=False))

            session.commit()
            print(f"[batch {batch_no}] {cur}–{end} OK")

            cur = end + 1

        print("Zliczono i usunięto paymenty (batched).")
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

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
    session = SessionLocal()
    existing = set(
        (v.language, v.subtitles, v.format)
        for v in session.query(Version.language, Version.subtitles, Version.format)
    )
    languages = ['polish', 'english', 'spanish', 'german']
    formats = ['2D', '3D', 'IMAX']
    versions = []
    for lang in languages:
        for subs in languages:
            for fmt in formats:
                if (lang, subs, fmt) not in existing:
                    versions.append(Version(language=lang, subtitles=subs, format=fmt))

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
        start_date = faker.date_between(start_date=datetime(2015, 1, 1), end_date="today")
        delta_days = faker.random_int(min=30, max=365)
        end_date = start_date + timedelta(days=delta_days)
        lic= License(
            title=faker.sentence(nb_words=2, variable_nb_words=True),
            director=faker.name(),
            duration_minutes=faker.random_int(min=60, max=200),
            license_number=number,
            start_date=start_date, 
            end_date=end_date,
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
            if not pair in already_exists:
                already_exists.add(pair)
                movie_versions.append(MovieVersion(fk_movie_id=pair[0], fk_version_id=pair[1]))
    seeder(movie_versions, "movie_version", len(movie_versions))

def seed_cinemas(n):
    session= SessionLocal()
    region_ids=[r[0] for r in session.query(Region._id).all()]
    cinemas=[Cinema(fk_region_id=random.choice(region_ids), city=faker.city(), street=faker.street_name(), building_number=random.randint(1, 30)) for _ in range(n)]
    seeder(cinemas, "cinema", n)

def seed_cinema_movie(min_mov=1, max_mov=10):
    session = SessionLocal()
    movie_ver_ids = [m[0] for m in session.query(MovieVersion._id).all()]
    cinema_ids = [c[0] for c in session.query(Cinema._id).all()]
    if not movie_ver_ids or not cinema_ids:
        print("Nie ma kin albo movie_version do seedowania")
        return
    already_exists = set(session.query(t_cinema_movie_version.c.fk_cinema_id,t_cinema_movie_version.c.fk_movie_version_id  ).all())
    new_records = []
    for c in cinema_ids:
        mv_ct= random.randint(min_mov, max_mov)
        for i in range(mv_ct): 
            pair = (c, random.choice(movie_ver_ids))
            if not pair in already_exists: 
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

def seed_room(min=1, max=5):
    session= SessionLocal()
    cinema_ids= [c[0] for c in session.query(Cinema._id).all()]
    already_exists = set(session.query(Room.fk_cinema_id, Room.number))
    rooms=[]
    for c in cinema_ids: 
        room_cts= random.randint(min, max)
        for i in range(room_cts):
            pair=(c, random.randint(1, 1000))
            if not pair in already_exists: 
                already_exists.add(pair)
                rooms.append(Room(fk_cinema_id=pair[0], number=pair[1]))
    seeder(rooms, "room", len(rooms))

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
    start_date_start = datetime(2015, 1, 1)
    start_date_end = start_date_start+timedelta(days=900)

    seeder((SpecialOffer(name = faker.word(),
                         start_time = faker.date_time_between(start_date=start_date_start, end_date=start_date_end).replace(second=0, microsecond=0),
                         end_time = faker.date_time_between(start_date=start_date_end+timedelta(days=1), end_date=datetime.now()+timedelta(days=180)).replace(second=0, microsecond=0),
                         amount = faker.random_int(min=1, max=10)
                         )
                         for _ in range(n)), "special_offer", n)

def seed_seat():
    session = SessionLocal()
    room_ids = [x[0] for x in session.query(Room._id).all()]

    if len(room_ids) == 0 :
        print("Brak id w room")
        session.close()
        return
    
    seats = []
    counter = 0
    for r in room_ids:
        seat_amount = random.randint(10, 30)
        for _ in range(seat_amount):
            counter += 1
            seats.append(Seat(fk_room_id = r,
                              seat_num = counter))
        if len(seats) > 50_000:
            seeder(seats, "seat", len(seats))
            seats = []
    seeder(seats, "seats", len(seats))
    session.close()

def seed_ticket():
    session = SessionLocal()

    # 1) Słowniki i proste struktury
    ticket_types = list(session.query(TicketType._id, TicketType.price))
    if not ticket_types:
        print("Brak id w ticket_type"); session.close(); return
    ticket_types_dict = {tid: price for tid, price in ticket_types}

    discounts = list(session.query(Discount._id, Discount.percentage))
    if not discounts:
        print("Brak id w discount"); session.close(); return
    discounts_dict = {did: pct for did, pct in discounts}

    # 2) Siedzenia zindeksowane po sali
    seats_by_room = defaultdict(list)
    for seat_id, room_id in session.query(Seat._id, Seat.fk_room_id):
        seats_by_room[room_id].append(seat_id)

    # 3) Płatności posortowane po czasie + bisect
    payments_raw = list(session.query(Payment._id, Payment.time_of_payment))
    if not payments_raw:
        print("Brak id w payment")
        session.close()
        return

    # 🔹 filtr: tylko płatności z ostatniego miesiąca
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    payments_raw = [p for p in payments_raw if p[1] >= month_ago]

    if not payments_raw:
        print("Brak płatności z ostatniego miesiąca")
        session.close()
        return

    # 🔹 sortujemy po czasie, żeby działał bisect
    payments_raw.sort(key=lambda x: x[1])
    payment_ids = [p[0] for p in payments_raw]
    payment_times = [p[1] for p in payments_raw]

    def random_valid_payment_id(t):
        """Zwraca losowy payment_id, którego czas jest nie późniejszy niż screening_time."""
        idx = bisect_right(payment_times, t)
        if idx == 0:
            return None
        return payment_ids[random.randrange(idx)]

    # 4) Statusy i wagi
    statuses_past = ['used', 'not_used']
    statuses_future = ['valid', 'reserved', 'payment_pending', 'free']
    statuses_future_weights = [1, 1, 1, 5]
    statuses_without_payment_etc = {'not_used', 'free'}  # zbiór tylko do membership O(1)

    # 5) Iteracja po seansach strumieniowo
    screenings_q = session.query(
        Screening._id, Screening.start_time, Screening.fk_room_id
    ).yield_per(10000)

    print("Wszystko jest w bazie więc tworzę tickety")
    tickets_batch = []
    batch_size = 50_000
    now = datetime.now()

    cnt = 0
    for screening_id, screening_time, room_id in screenings_q:
        is_future = screening_time > now
        seat_ids = seats_by_room.get(room_id)
        if not seat_ids:
            continue

        for seat_id in seat_ids:
            status = (
                random.choices(statuses_future, statuses_future_weights, k=1)[0]
                if is_future else random.choice(statuses_past)
            )

            ticket_type_id = None
            discount_id = None
            payment_id = None
            price = None

            if status not in statuses_without_payment_etc:
                # losowy rabat (albo brak)
                discount_id = None if random.random() < 0.5 else random.choice(list(discounts_dict.keys()))
                discount_pct = None if discount_id is None else discounts_dict[discount_id]

                # typ biletu i cena
                ticket_type_id = random.choice(list(ticket_types_dict.keys()))
                base_price = ticket_types_dict[ticket_type_id]
                price = base_price if discount_pct is None else base_price * (1 - discount_pct / 100)

                # płatność przed startem seansu
                payment_id = random_valid_payment_id(screening_time)

            tickets_batch.append(Ticket(
                fk_ticket_type_id=ticket_type_id,
                fk_seat_id=seat_id,
                fk_screening_id=screening_id,
                fk_discount_id=discount_id,
                fk_payment_id=payment_id,
                qr_code=faker.ean13(),
                status=status,
                price=price
            ))
            if len(tickets_batch) >= batch_size:
                seeder(tickets_batch, "ticket", len(tickets_batch))
                tickets_batch.clear()

        cnt += 1
        if cnt % 50000 == 0:
            print(f"Przetworzono {cnt:,} screeningów...")

    if tickets_batch:
        seeder(tickets_batch, "ticket", len(tickets_batch))

    session.close()


def seed_ticket_special_offer(n):
    session = SessionLocal()
    ticket_ids = [x[0] for x in session.query(Ticket._id).filter(Ticket.status.notin_(['not_used', 'free'])).all()]
    tickets = [x for x in session.query(Ticket._id, Payment.time_of_payment, Ticket.price).join(Ticket.fk_payment).filter(Ticket.status.notin_(["not_used", "free"])).all()]
    special_offer_ids = [x[0] for x in session.query(SpecialOffer._id, SpecialOffer.start_time, SpecialOffer.end_time, SpecialOffer.amount).all()]
    special_offers = [x for x in session.query(SpecialOffer._id, SpecialOffer.start_time, SpecialOffer.end_time, SpecialOffer.amount).all()]

    if len(ticket_ids) == 0 :
        print("Brak id w ticket")
        session.close()
        return
    
    if len(special_offer_ids) == 0 :
        print("Brak id w special_offer")
        session.close()
        return

    stmt = select(t_ticket_special_offer.c.fk_ticket_id, t_ticket_special_offer.c.fk_special_offer_id)
    ticket_special_offers = session.execute(stmt).fetchall()
    existed_pairs = {(r.fk_ticket_id, r.fk_special_offer_id) for r in ticket_special_offers}

    pairs = set()
    for _ in range(n):
        pair= (random.choice(tickets), random.choice(special_offers))
        if (pair[0][0], pair[1][0]) not in pairs and (pair[0][0], pair[1][0]) not in existed_pairs and (pair[1][2] >= pair[0][1] >= pair[1][1]):
            pairs.add((pair[0][0], pair[1][0]))
            special_offer_amount = pair[1][3]
            old_price = pair[0][2]
            session.execute(update(Ticket).where(Ticket._id == pair[0][0]).values(price = max(0, old_price - special_offer_amount)))

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

        
def _seed_users_base(ModelClass, n):
    session = SessionLocal()
    objects = []

    used_emails = {e for (e,) in session.query(User.email).all()}
    used_usernames = {u for (u,) in session.query(User.username).all()}

    for _ in range(n):
        base_email = faker.email()

        email = base_email
        email_counter = 1
        
        while email in used_emails:
            local_part, domain = base_email.split('@')
            email = f"{local_part}{email_counter}@{domain}"
            email_counter += 1
        used_emails.add(email)
        
        base_username = faker.user_name()
        username = base_username
        username_counter = 1
        
        while username in used_usernames:
            username = f"{base_username}{username_counter}"
            username_counter += 1
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
            "birthdate": faker.date_of_birth(minimum_age=16, maximum_age=60),
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

def _seed_workers_base(ModelClass, n):
    session = SessionLocal()
    objects = []

    used_emails = {e for (e,) in session.query(User.email).all()}
    used_usernames = {u for (u,) in session.query(User.username).all()}
    used_pesels = {u for (u,) in session.query(Worker.pesel_number).all()}
    used_bank_account_numbers = {u for (u,) in session.query(Worker.bank_account_number).all()}

    for _ in range(n):

        base_email = faker.email()

        email = base_email
        email_counter = 1
        
        while email in used_emails:
            local_part, domain = base_email.split('@')
            email = f"{local_part}{email_counter}@{domain}"
            email_counter += 1
        used_emails.add(email)
        
        base_username = faker.user_name()
        username = base_username
        username_counter = 1
        
        while username in used_usernames:
            username = f"{base_username}{username_counter}"
            username_counter += 1
        used_usernames.add(username)
        
        base_pesel = faker.pesel()
        pesel = base_pesel
        pesel_counter = 1
        
        while pesel in used_pesels:
            base = base_pesel[:-2]
            pesel = f"{base}{pesel_counter:02d}"
            pesel_counter += 1
        used_pesels.add(pesel)

        base_bank_acc = ''.join([str(random.randint(0, 9)) for _ in range(26)])
        bank_acc = base_bank_acc
        bank_acc_counter = 1
        
        while bank_acc in used_bank_account_numbers:
            base = base_bank_acc[:-4]
            bank_acc = f"{base}{bank_acc_counter:04d}"
            bank_acc_counter += 1
        used_bank_account_numbers.add(bank_acc)

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
    return _seed_users_base(Client, n)

def seed_regional_manager(n):
    return _seed_users_base(RegionalManager, n)
    
def seed_supervisor(n):
   return _seed_workers_base(Supervisor, n)

def seed_service(n):
   return _seed_workers_base(Service, n)

def _employment_overlaps(start1, end1, start2, end2):
    end1_actual = end1 or datetime.today().date()
    end2_actual = end2 or datetime.today().date()
    
    return (start1 < end2_actual) and (start2 < end1_actual)

def seed_employment_with_shifts(n_employments, min_shifts=10, max_shifts=100):
    session = SessionLocal()

    worker_ids = [w[0] for w in session.query(Worker._id).all()]
    cinema_ids = [c[0] for c in session.query(Cinema._id).all()]
    
    shift_slots = [('08:00', '16:00'), ('10:00', '18:00')]
    shift_types = ['cashier', 'usher', 'cleaning', 'projection', 'technical_support']

    if not worker_ids or not cinema_ids:
        print("Brakuje workerów lub kin — seeduj je najpierw!")
        session.close()
        return
    
    existing_employments = session.query(Employment).all()
    
    workers_with_active_employment = set()
    for emp in existing_employments:
        if emp.end_date is None:
            workers_with_active_employment.add(emp.fk_worker_id)

    employments = []
    all_shifts = []
    n_all_shifts = 0
    skipped = 0
    
    for _  in range(n_employments):
        worker_id = random.choice(worker_ids)
        cinema_id = random.choice(cinema_ids)


        
        start_date = faker.date_between(start_date='-5y', end_date='-1y')


        if random.random() < 0.3 or worker_id in workers_with_active_employment:
            months = random.randint(6, 24)
            end_date = start_date + timedelta(days=30 * months)
            if end_date > datetime.today().date():
                end_date = datetime.today().date()
        else:
            end_date = None
        
        
        # SPRAWDZENIE 2: Czy nakłada się z istniejącymi employmentami?
        worker_existing_emps = [e for e in existing_employments if e.fk_worker_id == worker_id]
        overlaps = any(
            _employment_overlaps(start_date, end_date, emp.start_date, emp.end_date)
            for emp in worker_existing_emps
        )
        
        if overlaps:
            skipped += 1
            continue
        
        emp = Employment(
            fk_worker_id=worker_id,
            fk_cinema_id=cinema_id,
            start_date=start_date,
            end_date=end_date
        )
        if (end_date == None):
            workers_with_active_employment.add(worker_id)
            
        employments.append(emp)
        existing_employments.append(emp)
        
        employment_end = end_date or datetime.today().date()
        total_days = (employment_end - start_date).days
        
        n_shifts = min(total_days, random.randint(min_shifts, max_shifts))
        n_all_shifts += n_shifts
        all_days = [start_date + timedelta(days=x) for x in range(total_days)]
        selected_days = random.sample(all_days, n_shifts)

        for day in selected_days:
            start_hour, end_hour = random.choice(shift_slots)
            
            start_time = datetime.combine(day, datetime.strptime(start_hour, '%H:%M').time())
            end_time = datetime.combine(day, datetime.strptime(end_hour, '%H:%M').time())

            shift = Shift(
                fk_worker_id=worker_id,
                start_time=start_time,
                end_time=end_time,
                type=random.choice(shift_types)
            )
            all_shifts.append(shift)  
      
    print(f"Skipped {skipped} employmentów z powodu nakładania się lub aktywnych employmentów")
    try:
        session.add_all(employments)
        session.add_all(all_shifts)
        session.commit()
        print(f"Dodano {n_employments - skipped} rekordów do Employment i {n_all_shifts} rekordów do Shift!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally:
        session.close()

def make_batch(function, size):
    batch_size = 50_000
    if size > 50_000:
        for i in range(0, size, batch_size):
            current_batch = min(batch_size, size - i)
            function(current_batch)
    else:
        function(size)


if __name__ == "__main__":
    seed_special_offer(1000000); 
    # print("ZACZYNAM SEEDOWANIE")

    # REGION = 16
    # PRODUCT = 1000
    # MOVIE_AND_LICENSE = 10_000
    # min_versions = 1
    # max_versions = 5
    # min_cinema_movie_version=10
    # max_cinema_movie_version=50 
    # CINEMA = 500
    # SERVICE = 100_000
    # SUPERVISOR = 5000
    # CLIENT = 1_000_000
    # REGIONAL_MANAGER = 500
    # # SHIFT = 200_000
    # EMPLOYMENT = 150_000
    # SCREENING = 2_000_000
    # PAYMENT = 10_000_000
    # PRODUCT_SALE = 1_000_000
    # TERM = 700
    # SPECIAL_OFFER = 10_000
    # TICKET_SPECIAL_OFFER = 2_000_000
    

    # # nie potrzebują innych tabel
    # make_batch(seeder_region, REGION)
    # make_batch(seeder_product, PRODUCT)

    # make_batch(seed_license, MOVIE_AND_LICENSE)
    # seed_version()
    # seed_movie_version(min_versions, max_versions)

    # # # wymaga: region
    # make_batch(seed_cinemas, CINEMA)
    # seed_cinema_movie(min_cinema_movie_version, max_cinema_movie_version)
    # seed_room(2, 8)
   
    # make_batch(seed_service, SERVICE)
    # make_batch(seed_supervisor, SUPERVISOR)
    # make_batch(seed_client, CLIENT)
    # make_batch(seed_regional_manager, REGIONAL_MANAGER)
    # make_batch(seed_employment_with_shifts, EMPLOYMENT)

    # # # wymaga: room, movie_version
    # make_batch(seeder_screening, SCREENING)

    # # # wymaga: client
    # make_batch(seeder_payment, PAYMENT)

    # # # wymaga: product, payment, cinema
    # make_batch(seeder_product_sale, PRODUCT_SALE)

    # # # wymaga: region, regional_manager
    # make_batch(seeder_term, TERM)

    # make_batch(seed_special_offer, SPECIAL_OFFER)
    # seed_discount() 
    # seed_ticket_type()

    # # # wymaga: room
    # seed_seat()

    # # wymaga: ticket_type, discount, payment, seat, screening
    # seed_ticket()

    # # wymaga: ticket, special_offer
    # make_batch(seed_ticket_special_offer, TICKET_SPECIAL_OFFER)
    # calculate_payments()