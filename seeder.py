from db.connection import SessionLocal
from db.models import *
from faker import Faker 
import random
from datetime import timedelta

faker= Faker()

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

def seeder_region(n):
    session = SessionLocal()
    existing_names = set(t.name for t in session.query(Region).all())
    names = set()
    for _ in range(n):
        name = faker.state()
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

        if name in names or name in existing_names:
            continue

        if barcode is not None and (barcode in barcodes or barcode in existing_barcodes):
            continue
            
        names.add(name)

        if barcode is not None:
            barcodes.add(barcode)
        products.append(Product(name = name, barcode = barcode, price = price))

    session.close()
    seeder(products, "product", len(products))

def seeder_screening(n):
    session = SessionLocal()
    screenings = []
    room_ids = [x._id for x in session.query(Room).all()]
    movie_version_ids = [x._id for x in session.query(MovieVersion).all()]

    if(len(room_ids) == 0):
        print("Brak danych w tabeli Room")
        session.close()
        return
    if(len(movie_version_ids) == 0):
        print("Brak danych w tabeli MovieVersion")
        session.close()
        return
    
    for _ in range(n):
        fk_room_id = random.choice(room_ids)
        fk_movie_version_id = random.choice(movie_version_ids)
        start_time = faker.date_time_between(start_date='1970-01-01', end_date='now')
        start_time = start_time.replace(second=0, microsecond=0)
        movie_version = session.query(MovieVersion).get(fk_movie_version_id)
        movie = session.query(Movie).get(movie_version.fk_movie_id)
        duration = movie.duration_minutes
        end_time = start_time + timedelta(minutes = duration + 40)
        screenings.append(Screening(fk_room_id = fk_room_id, fk_movie_version_id = fk_movie_version_id, start_time = start_time, end_time = end_time))
    session.close()
    seeder(screenings, "screening", len(screenings))

def seeder_product_sale(n):
    product_sales = []
    session = SessionLocal()
    product_ids = [t._id for t in session.query(Product).all()]
    payment_ids = [t._id for t in session.query(Payment).all()]
    cinema_ids = [t._id for t in session.query(Cinema).all()]

    if(len(product_ids) == 0):
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
        fk_product_id = random.choice(product_ids)
        fk_payment_id = random.choice(payment_ids)
        fk_cinema_id = random.choice(cinema_ids)
        time_of_sale = faker.date_time_between(start_date='1970-01-01', end_date='now')
        time_of_sale = time_of_sale.replace(microsecond=0)
        product_sales.append(ProductSale(fk_product_id = fk_product_id, fk_payment_id = fk_payment_id, fk_cinema_id = fk_cinema_id, time_of_sale = time_of_sale))
    session.close()
    seeder(product_sales, "product_sale", n)

def seeder_payment(n):
    payments = []
    session = SessionLocal()
    client_ids = [t._id for t in session.query(Client).all()]

    if(len(client_ids) == 0):
        print("Brak danych w tabeli Client")
        session.close()
        return
    
    for _ in range(n):
        fk_client_id = random.choice(client_ids)
        type = random.choice(['cash', 'card', 'blik', 'online', 'voucher'])
        amount = faker.pyfloat(min_value=10, max_value=1000, right_digits=2, positive=True)
        payments.append(Payment(fk_client_id = fk_client_id, type = type, amount = amount))
    session.close()
    seeder(payments, "payment", n)

def seeder_regional_manager(n):
    regional_managers = []
    session = SessionLocal()
    existing_regional_managers_ids = set(t._id for t in session.query(RegionalManager).all())
    regional_managers_ids = set()
    user_ids = [t._id for t in session.query(User).all()]

    if(len(user_ids) == 0):
        print("Brak danych w tabeli User")
        session.close()
        return
    
    for _ in range(n):
        fk_user_id = random.choice(user_ids)
        if fk_user_id not in existing_regional_managers_ids and fk_user_id not in regional_managers_ids:
            regional_managers_ids.add(fk_user_id)
            regional_managers.append(RegionalManager(_id = fk_user_id))
    session.close()
    seeder(regional_managers, "regional_manager", len(regional_managers))

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
    
    for _ in range(n):
        fk_region_id = random.choice(region_ids)
        fk_manager_id = random.choice(regional_manager_ids)
        start_date = faker.date_between(start_date='1970-01-01', end_date='2026-01-01')
        end_date = faker.date_between(start_date='1970-01-01', end_date='2026-01-01')
        if end_date < start_date:
            end_date = None
        terms.append(Term(fk_region_id = fk_region_id, fk_manager_id = fk_manager_id, start_date = start_date, end_date = end_date))

    session.close()
    seeder(terms, "term", n)
    
if __name__ == "__main__":
    print("Zaczynam seedowanie")
    seeder_region(5000)
    seeder_product(5000)
    #seeder_screening(1000000)
    #seeder_product_sale(1000000)
    #seeder_payment(1000000)
    #seeder_regional_manager(5000)
    #seeder_term(20000)
