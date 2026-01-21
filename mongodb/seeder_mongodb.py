import random
from faker import Faker
from decimal import Decimal
from bson import ObjectId, Decimal128
from bson.decimal128 import Decimal128
from pymongo import MongoClient, errors
from datetime import timedelta, datetime

#CONFIG
fake = Faker(['pl_PL']) 
client = MongoClient("mongodb://localhost:27017/")
db = client["cinema_mongodb_local"]
#CONFIG

#CONST
WORKER_TYPES = ['service', 'supervisor']
MANAGER_TYPE = 'regional_manager'
CLIENT_TYPE = 'client'
SHIFT_TYPES = ['cashier', 'usher', 'cleaner', 'projection', 'technical_support']
PAYMENT_TYPES = ["blik", "cash", "card", "online", "voucher"]
ORDER_STATUSES = ["reserved", "pending", "paid"]
#CONST


def get_versions_pool(pool_size):
    languages = ["PL", "EN", "GER", "FR", "ES"]
    subtitles_opts = ["NO", "PL", "EN"]
    formats = ["2D", "3D", "IMAX"]
    
    result = []
    for _ in range(pool_size):
        version = {
            "language": random.choice(languages),
            "subtitles": random.choice(subtitles_opts),
            "format": random.choice(formats) 
        }
        result.append(version)
    return result

#CONST
VERSIONS = get_versions_pool(10)
#CONST

#Helper
def generate_taken_seats(room_capacity=100, active = False):
    taken_seats = []
    seats_to_take = random.randint(0, room_capacity)
    
    seat_numbers = random.sample(range(1, room_capacity + 1), seats_to_take)
    status_col=["paid"]
    if active: 
        status_col.append("reserved")

    
    for number in seat_numbers:
        taken_seats.append({
            "seat_number": number,
            "status": random.choice(status_col)
        })
    return taken_seats

#Batchable functions 
def seed_movies_and_screenings(movies_count=1000, screenings_count =100000):    
    versions_pool = VERSIONS
    
    movies_batch = []
    screenings_archive_batch = []
    screenings_active_batch = []
    #MOVIE
    for _ in range(movies_count):
        num_versions_for_movie = random.randint(1, 5)
        movie_versions = random.choices(versions_pool, k=num_versions_for_movie)

        start_date = fake.date_time_between(start_date='-10y', end_date='now')
        duration_days = random.randint(365, 365 * 5) 
        end_date = start_date + timedelta(days=duration_days)

        cost_value = str(round(random.uniform(10000.00, 100000.00), 2))

        movie = {
            "_id": ObjectId(),
            "title": fake.word().title(),
            "director": f"{fake.first_name()} {fake.last_name()}",
            "duration_minutes": random.randint(60, 180),
            "versions": movie_versions,
            "license": {
                "number": fake.uuid4(), 
                "start_date": start_date, 
                "end_date": end_date,
                "cost": Decimal128(cost_value) 
            }
        }
        movies_batch.append(movie)

    #SCREENING
    cinemas = list(db.cinema.find({}, {"_id": 1, "rooms": 1}))
    now =datetime.now()
    for i in range(screenings_count):
        selected_cinema = random.choice(cinemas)
        selected_cinema_id = selected_cinema["_id"]
        selected_room = random.choice(selected_cinema["rooms"])
        seats_count= len(selected_room["seats"])
        selected_movie = random.choice(movies_batch)
        screening_start = fake.date_time_between(
            start_date=selected_movie["license"]["start_date"], 
            end_date=selected_movie["license"]["end_date"]
        )
        screening_end = screening_start + timedelta(minutes=selected_movie["duration_minutes"])
        version_snapshot = random.choice(selected_movie["versions"])

        active=  not (screening_end < now) 
        screening = {
            "cinema_id": selected_cinema_id,
            "start_time": screening_start,
            "end_time": screening_end,
            "movie_id": selected_movie["_id"],
            "movie_title": selected_movie["title"], 
            "version_snapshot": version_snapshot,   
            "room_number": selected_room["room_number"],
            "taken_seats": generate_taken_seats(room_capacity=seats_count, active=active) 
        }
        if screening_start < now:
            screenings_archive_batch.append(screening)
        else:
            screenings_active_batch.append(screening)
    
    #Save
    if movies_batch:
        db.movie.insert_many(movies_batch)
        print(f"Dodano {len(movies_batch)} filmów.")
        
    if screenings_active_batch:
        db.screening.insert_many(screenings_active_batch)
        print(f"Dodano {len(screenings_active_batch)} AKTYWNYCH seansów.")

    if screenings_archive_batch:
        db.screening_archive.insert_many(screenings_archive_batch)
        print(f"Dodano {len(screenings_archive_batch)} ARCHIWALNYCH seansów.")

def seed_ticket_type():
    existing_names = set(db.ticket_type.distinct("name"))
    ticket_types = []

    if "standard" not in existing_names:
        ticket_types.append({
            "name": "standard",
            "base_price": Decimal128("30.00")
            })

    if "vip" not in existing_names:
        ticket_types.append({
            "name": "vip",
            "base_price": Decimal128("35.00")
            })

    if ticket_types:
        try:
            db.ticket_type.insert_many(ticket_types)
            print(f"Sukces: Dodano {len(ticket_types)} ticket_type.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy ticket_type!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")

def seed_discount(): 
    existing_names = set(db.discount.distinct("name"))
    discounts = []

    if "student" not in existing_names:
        discounts.append({
            "name": "student",
            "percentage": Decimal128("21.00")
        })

    if "senior" not in existing_names:
        discounts.append({
            "name": "senior",
            "percentage": Decimal128("12.00")
        })

    if "military" not in existing_names:
        discounts.append({
            "name": "military",
            "percentage": Decimal128("10.00")
        })

    if discounts:
        try:
            db.discount.insert_many(discounts)
            print(f"Sukces: Dodano {len(discounts)} discount.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy discount!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")

def seed_group_type():
    existing_names = set(db.group_type.distinct("name"))
    group_types = []

    if "pojedynczy" not in existing_names:
        group_types.append({
            "name": "single",
            "discount_percentage": Decimal128("0.00"),
            "min_size": 1
        })

    if "podwójny" not in existing_names:
        group_types.append({
            "name": "double",
            "discount_percentage": Decimal128("5.00"),
            "min_size": 2
        })

    if "rodzinny" not in existing_names:
        group_types.append({
            "name": "family",
            "discount_percentage": Decimal128("10.00"),
            "min_size": 3
        })

    if "grupowy" not in existing_names:
        group_types.append({
            "name": "group",
            "discount_percentage": Decimal128("30.00"),
            "min_size": 10
        })

    if group_types:
        try:
            db.group_type.insert_many(group_types)
            print(f"Sukces: Dodano {len(group_types)} group_type.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy group_type!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")

def seed_special_offer(count = 10): 
    special_offers = []

    for _ in range(count):
        start_range = datetime.today() - timedelta(days=3650)
        end_range = datetime.today() + timedelta(days=90)
        duration = fake.random_int(min=10, max=900)

        start_time = fake.date_time_between(start_date=start_range, end_date=end_range).replace(second=0, microsecond=0)

        end_time = fake.date_time_between(start_date=start_time, end_date=start_time + timedelta(days=duration)).replace(second=0, microsecond=0)

        special_offer_doc = {
            "name": fake.word(),
            "start_time": start_time,
            "end_time": end_time,
            "amount": fake.random_int(min=1, max=10)
        }

        special_offers.append(special_offer_doc)

    if special_offers:
        try:
            db.special_offer.insert_many(special_offers)
            print(f"Sukces: Dodano {len(special_offers)} special_offer.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy special_offer!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")

def seed_product(count = 10):
    existing_names = set(db.product.distinct("name"))
    existing_barcodes = set(db.product.distinct("barcode"))
    names = set()
    barcodes = set()
    products = []

    for _ in range(count):
        name = fake.word()
        barcode = fake.ean13() if random.random() > 0.2 else None
        price = Decimal128(f"{fake.pyfloat(min_value=2, max_value=100, right_digits=2, positive=True):.2f}")
        is_available = fake.boolean()

        if name in names or name in existing_names:
            continue

        if barcode is not None and (barcode in barcodes or barcode in existing_barcodes):
            continue

        names.add(name)

        if barcode is not None:
            barcodes.add(barcode)

        product_doc = {}
        product_doc["name"] = name
        if barcode is not None:
            product_doc["barcode"] = barcode
        product_doc["is_available"] = is_available
        product_doc["price"] = price

        products.append(product_doc)

    if products:
        try:
            db.product.insert_many(products)
            print(f"Sukces: Dodano {len(products)} product.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy product!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")

def seed_cinema(cinema_count = 10, max_room_count = 10, max_seat_count = 10):
    cinemas = []
    max_room_count = max(2, max_room_count)
    max_seat_count = max(10, max_seat_count)

    for _ in range(cinema_count):
        rooms = []
        room_count = fake.random_int(min=2, max=max_room_count)
        for room in range(room_count):
            seats = []
            seat_count = fake.random_int(min=10, max=max_seat_count)
            for seat in range(seat_count):
                seat_doc = {"seat_number": seat + 1}
                seats.append(seat_doc)
            room_doc = {"_id": ObjectId(), "room_number": room + 1, "seats": seats}
            rooms.append(room_doc)
        cinema_doc = {
            "city": fake.city(),
            "street": fake.street_name(),
            "building_number": str(fake.building_number()),
            "rooms": rooms,
            "region_name": fake.administrative_unit()
        }
        cinemas.append(cinema_doc)
                
    if cinemas:
        try:
            db.cinema.insert_many(cinemas)
            print(f"Sukces: Dodano {len(cinemas)} cinema.")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy cinema!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")

def product_snapshot_for_order(product_list):
    product_snapshot_list = []
    product_snapshot_total_price = 0

    product_snapshot_amount = random.randint(1, 4)
    for _ in range(product_snapshot_amount):
        product_for_snapshot = random.choice(product_list)
        
        count = random.randint(1, 4)
        product_snapshot = {
            "product_id": product_for_snapshot["_id"],
            "name": product_for_snapshot["name"],
            "count": count,
            "price": Decimal128(product_for_snapshot["price"].to_decimal()*count),
        }
        product_snapshot_total_price += product_snapshot["price"].to_decimal()
        product_snapshot_list.append(product_snapshot)
    
    return product_snapshot_list, product_snapshot_total_price

def ticket_for_order(taken_seats_from_screening, screening_id, movie_title, group_type_list, special_offer_list, ticket_type_list, discount_list, order_status, is_archive):
    ticket_list = []
    tickets_total_price = 0

    current_taken_seat_index = 0
    total_seats_count = len(taken_seats_from_screening)
    while current_taken_seat_index < total_seats_count:
        seats_remaining = total_seats_count - current_taken_seat_index

        possible_group_type = [g for g in group_type_list if g["min_size"] <= seats_remaining]

        group_type_for_ticket = random.choice(possible_group_type)
        group_type_discount_percentage = group_type_for_ticket["discount_percentage"]

        ticket_seats_amount = group_type_for_ticket["min_size"]
        if ticket_seats_amount > seats_remaining:
            ticket_seats_amount = seats_remaining

        ticket_status = "valid"

        if order_status == "reserved":
            ticket_status = "reserved"

        if is_archive:
            ticket_status = "used" if random.random() >= 0.02 else "not_used"

        group_type_snapshot = {
            "_id": group_type_for_ticket["_id"],
            "name": group_type_for_ticket["name"],
            "discount_percentage": group_type_discount_percentage
        }

        seats_snapshot = []
        ticket_price = 0
        for i in range(ticket_seats_amount):
            actual_seat_number = taken_seats_from_screening[current_taken_seat_index + i]

            ticket_type_for_seat = random.choice(ticket_type_list)
            seat_price = ticket_type_for_seat["base_price"]
            seat_price_for_total = (1 - group_type_discount_percentage.to_decimal()/100)*seat_price.to_decimal()
            
            
            seat = {
                "seat_number": actual_seat_number,
                "ticket_type_id": ticket_type_for_seat["_id"],
                "ticket_type": ticket_type_for_seat["name"],
                "ticket_base_price": seat_price,
            }
            if random.random() >= 0.7:
                dicsount_for_seat = random.choice(discount_list)
                seat["discount_id"] = dicsount_for_seat["_id"]
                seat["discount_name"] = dicsount_for_seat["name"]
                seat["discount_percentage"] = dicsount_for_seat["percentage"]
                seat_price_for_total = (1 - dicsount_for_seat["percentage"].to_decimal()/100)*seat_price.to_decimal()
            
            ticket_price += seat_price_for_total
            seats_snapshot.append(seat)

        if special_offer_list:
            special_offer_for_ticket = random.choice(special_offer_list)
            special_offer_id = special_offer_for_ticket["_id"]
            special_offer_amount = special_offer_for_ticket["amount"]

            special_offer_total_minus = special_offer_amount * ticket_seats_amount
            ticket_price -= special_offer_total_minus
        if ticket_price < 0:
            ticket_price = 0
        ticket = {
            "total_price": Decimal128(ticket_price),
            "qr_code": fake.uuid4(),
            "status": ticket_status,
            "group_type_snapshot": group_type_snapshot,
            "screening_id": screening_id,
            "movie_title": movie_title,
            "seats_snapshot": seats_snapshot
        }
        if special_offer_list:
            ticket["special_offer_id"] = special_offer_id
            ticket["special_offer_amount"] = Decimal128(str(special_offer_total_minus))

        tickets_total_price += ticket_price
        ticket_list.append(ticket)
        current_taken_seat_index += ticket_seats_amount
    return ticket_list, tickets_total_price

def seed_order(batch_size): 
    user_ids = [user["_id"] for user in db["user"].find({"type": "client"}, {"_id": 1})]
    cinema_ids = [cinema["_id"] for cinema in db["cinema"].find({}, {"_id": 1})]

    product_list = list(db["product"].find())
    group_type_list = list(db["group_type"].find())
    ticket_type_list = list(db["ticket_type"].find())
    discount_list = list(db["discount"].find())

    special_offer_list = list(db["special_offer"].find({}, {"_id": 1, "start_time": 1, "amount": 1}).sort("start_time", 1))

    screening_sources = (("screening_archive", True), ("screening", False))

    order_list = []
    count = 0

    for curr_screening_list, is_archive in screening_sources:
        screening_cursor = db[curr_screening_list].find({}, {"_id": 1, "movie_title": 1, "taken_seats": 1, "start_time": 1}).batch_size(1000)
        for screening in screening_cursor:
            screening_start_time = screening["start_time"]
            filtered_special_offer_list = [offer for offer in special_offer_list if offer["start_time"] < screening_start_time]

            taken_seats = screening.get("taken_seats", [])
            if not taken_seats:
                continue
            taken_seats_numbers = [seat["seat_number"] for seat in taken_seats]
            total_seats_amount = len(taken_seats_numbers)

            curr_idx = 0

            while curr_idx < total_seats_amount:
                order_amount = 0
                order_status = "paid" if is_archive else random.choices(ORDER_STATUSES, weights=[4, 1, 95], k=1)[0]
                order_seats_amount = random.randint(1, 10)
                end_idx = min(curr_idx + order_seats_amount, total_seats_amount)

                seats_chunk_for_order = taken_seats_numbers[curr_idx : end_idx]

                tickets, tickets_total_price = ticket_for_order(
                    taken_seats_from_screening=seats_chunk_for_order,
                    screening_id=screening["_id"],
                    movie_title=screening["movie_title"],
                    group_type_list=group_type_list,
                    special_offer_list=filtered_special_offer_list,
                    ticket_type_list=ticket_type_list,
                    discount_list=discount_list,
                    order_status=order_status,
                    is_archive=is_archive
                )

                order_amount += tickets_total_price

                order = {
                    "_id": ObjectId(),
                    "cinema_id": random.choice(cinema_ids),
                    "status": order_status,
                    "ticket": tickets,
                }

                if random.random() >= 0.2:
                    order["user_id"] = random.choice(user_ids)

                if order_status != "reserved":
                    order["time_of_payment"] = screening_start_time - timedelta(minutes=random.randint(15, 14*24*60))
                    order["payment_type"] = random.choice(PAYMENT_TYPES)

                    #PRODUCT_SNAPSHOT
                    product_snapshot_prob = random.random()
                    if product_snapshot_prob >= 0.7:
                        product_snapshot_list, product_snapshot_total_price = product_snapshot_for_order(product_list)
                        order_amount += product_snapshot_total_price
                        order["product_snapshot"] = product_snapshot_list
                    #PRODUCT_SNAPSHOT

                order["amount"] = Decimal128(order_amount)

                order_list.append(order)
                curr_idx = end_idx

                if len(order_list) > batch_size:
                    try:
                        db["order"].insert_many(order_list)
                        order_list = []
                        count += 1
                        print(f"{count}. Zapisano {batch_size} order")
                    except errors.BulkWriteError as bwe:
                        print("Błąd walidacji przy order!")
                        print(bwe.details['writeErrors'][0])
                    except Exception as e:
                        print(f"Inny błąd: {e}")
    if order_list:
        try:
            db["order"].insert_many(order_list)
            count += 1
            print(f"{count}. Zapisano {len(order_list)} order")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy order!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")

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

def clear_mongodb():
    collections = db.list_collection_names()
    count = 1
    for collection_name in collections:
        if collection_name.startswith("system."):
            continue
        try:
            db[collection_name].delete_many({})
            print(f"{count}. Wyczyszczono {collection_name}")
            count += 1
        except Exception as e:
            print(f"Błąd przy usuwaniu: {e}")
    print("")


if __name__=="__main__": 
    clear_mongodb()

    seed_cinema(100, 10, 50)
    seed_discount()
    seed_group_type()
    seed_special_offer(10_000)
    seed_ticket_type()
    seed_product(1000)
    for _ in range (15):
        seed_movies_and_screenings(7000, 100_000)
    for _ in range(25):
        seed_clients(100_000)
    seed_managers(50)
    seed_workers_with_shifts(10_000)
    seed_order(2000)