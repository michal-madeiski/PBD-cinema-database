from db.connection import SessionLocal
from db.models import User, Client, Worker, Service, Supervisor, Employment, Shift, RegionalManager, Cinema
from faker import Faker 
import random
import datetime

faker = Faker('pl_PL')

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
        
import pytz
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
            now_minus_5h = datetime.datetime.now() - datetime.timedelta(hours=5)
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
            now_minus_5h = datetime.datetime.now() - datetime.timedelta(hours=5)
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
            end_date = start_date + datetime.timedelta(days=30 * months)
            if end_date > datetime.date.today():
                end_date = datetime.date.today()
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


from datetime import timedelta

def seed_shifts(n):
    session = SessionLocal()

    worker_ids = [w[0] for w in session.query(Worker._id).all()]
    if not worker_ids:
        print("Brak workerów — seeduj workerów najpierw!")
        session.close()
        return

    SHIFT_TYPES = ['cashier', 'usher', 'cleaning', 'projection', 'technical_support']

    shifts = []

    for _ in range(n):
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

    try:
        session.add_all(shifts)
        session.commit()
        print(f"Dodano {n} rekordów do Shift!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally:
        session.close()



if __name__ == "__main__":
    print("Zaczynam seedowanie")
    # seed_service(100000)
    # seed_supervisor(10)
    # seed_client(10000)
    # seed_regional_manager(100)


    
    
