import random
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId, Decimal128
from pymongo import MongoClient, errors
from faker import Faker

#CONFIG 
fake = Faker(['pl_PL']) 
client = MongoClient("mongodb://localhost:27017/")
db = client["cinema_db"]

WORKER_TYPES = ['service', 'supervisor']
MANAGER_TYPE = 'regional_manager'
CLIENT_TYPE = 'client'
SHIFT_TYPES = ['cashier', 'usher', 'cleaner', 'projection', 'technical_support']


def get_cinema_ids():
    cinemas = list(db.cinema.find({}, {"_id": 1}))
    return [c["_id"] for c in cinemas]


def seed_workers_with_shifts(count=10):
    cinema_ids = get_cinema_ids()
    
    if not cinema_ids:
        print("Brak kin w bazie! Nie można seedować pracowników.")
        return
        
    print(f"--- Generowanie {count} pracowników (Service/Supervisor) ---")
    
    workers = []
    shifts = []

    for _ in range(count):
        user_id = ObjectId()
        user_type = random.choice(WORKER_TYPES)
        
        create_date = fake.date_between(start_date='-10y', end_date='-2y')
        create_datetime = datetime.combine(create_date, datetime.min.time())
        
        salary_py = Decimal(random.randrange(350000, 850000)) / 100
        salary_bson = Decimal128(salary_py)

        user_doc = {
            "_id": user_id,
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "birthdate": datetime.combine(fake.date_of_birth(minimum_age=18, maximum_age=50), datetime.min.time()),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.sha256(),
            "account_create_date": create_datetime,
            "last_login_date": fake.date_time_between(start_date=create_date, end_date='now'),
            "type": user_type,
            "pesel_number": fake.pesel(),
            "bank_account_number": fake.iban(),
            "salary_month": salary_bson,
            "employments": []
        }

        num_employments = random.randint(1, 4)
        current_date = create_date
        shift_slots = [('08:00', '16:00'), ('10:00', '18:00'), ('14:00', '22:00')]

        for _ in range(num_employments):
            duration = random.randint(90, 400)
            t_start = datetime.combine(current_date, datetime.min.time())
            t_end_date = current_date + timedelta(days=duration)
            
            assigned_cinema = random.choice(cinema_ids)
            is_active = t_end_date >= datetime.now().date()
            
            emp_doc = {"start_date": t_start, "cinema_id": assigned_cinema}
            if not is_active:
                emp_doc["end_date"] = datetime.combine(t_end_date, datetime.min.time())
            
            user_doc["employments"].append(emp_doc)

            limit_date = datetime.now().date() if is_active else t_end_date
            total_days = (limit_date - current_date).days
            
            if total_days > 0:
                s_count = min(total_days, random.randint(10, 30))
                days = random.sample([current_date + timedelta(days=d) for d in range(total_days)], s_count)

                for day in days:
                    slot_start, slot_end = random.choice(shift_slots)
                    s_start = datetime.combine(day, datetime.strptime(slot_start, '%H:%M').time())
                    s_end = datetime.combine(day, datetime.strptime(slot_end, '%H:%M').time())
                    
                    shifts.append({
                        "start_time": s_start,
                        "end_time": s_end,
                        "type": random.choice(SHIFT_TYPES),
                        "worker_id": user_id,
                        "cinema_id": assigned_cinema
                    })

            if is_active:
                break
            current_date = t_end_date + timedelta(days=random.randint(2, 14))

        workers.append(user_doc)

    if workers:
        try:
            db.user.insert_many(workers)
            print(f"Dodano {len(workers)} pracowników.")
            if shifts:
                db.shift.insert_many(shifts)
                print(f"Dodano {len(shifts)} zmian (shifts).")
        except errors.BulkWriteError as bwe:
            print("Błąd zapisu (Schema Validation?):")
            print(bwe.details['writeErrors'][0])

def seed_managers(count=5):
    print(f"--- Generowanie {count} managerów ---")
    managers = []
    for _ in range(count):
        create_date = fake.date_between(start_date='-10y', end_date='-4y')
        
        num_terms = random.randint(1, 4)
        current_date = create_date
        terms = []

        for _ in range(num_terms):
            duration = random.randint(180, 400)
            t_start = datetime.combine(current_date, datetime.min.time())
            t_end = current_date + timedelta(days=duration)
            
            doc = {"start_date": t_start, "region_name": fake.administrative_unit()}
            
            if t_end < datetime.now().date():
                doc["end_date"] = datetime.combine(t_end, datetime.min.time())
                terms.append(doc)
                current_date = t_end + timedelta(days=1)
            else:
                terms.append(doc)
                break

        user_doc = {
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "birthdate": datetime.combine(fake.date_of_birth(minimum_age=25, maximum_age=65), datetime.min.time()),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.sha256(),
            "account_create_date": datetime.combine(create_date, datetime.min.time()),
            "last_login_date": fake.date_time_between(start_date=create_date, end_date='now'),
            "type": MANAGER_TYPE,
            "terms": terms
        }
        managers.append(user_doc)
    
    if managers:
        try:
            db.user.insert_many(managers)
            print(f"Sukces: Dodano {len(managers)} menadżerów.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy menadżerach!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")


def seed_clients(count=50):
    print(f"--- Generowanie {count} klientów ---")
    clients = []
    for _ in range(count):
        create_date = fake.date_between(start_date='-5y', end_date='-4y')
        
        user_doc = {
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "birthdate": datetime.combine(fake.date_of_birth(minimum_age=13, maximum_age=90), datetime.min.time()),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.sha256(),
            "account_create_date": datetime.combine(create_date, datetime.min.time()),
            "last_login_date": fake.date_time_between(start_date=create_date, end_date='now'),
            "type": CLIENT_TYPE
        }
        clients.append(user_doc)
    
    if clients:
        try:
            db.user.insert_many(clients)
            print(f"Sukces: Dodano {len(clients)} klientów.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy klientach!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")


def seed_smth(arg="piszemy sparametryzowane"): 
    pass 



if __name__=="__main__": 
    # seed_managers(100)
    # seed_workers_with_shifts(50000) #POTRZEBUJE CINEMA!!!
    # seed_clients(200_000)
    
    # db.user.delete_many({})
    # db.shift.delete_many({})
    print("Koniec.")