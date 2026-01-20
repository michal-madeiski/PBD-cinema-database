import random
from pymongo import MongoClient, errors
from faker import Faker
from datetime import datetime, timedelta
from bson.decimal128 import Decimal128
from bson import ObjectId

#CONFIG 
fake = Faker(['pl_PL']) 
client = MongoClient("mongodb://localhost:27017/")
db = client["cinema_db"]

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
            "name": "pojedynczy",
            "discount_percentage": Decimal128("0.00"),
            "min_size": 1
        })

    if "podwójny" not in existing_names:
        group_types.append({
            "name": "podwójny",
            "discount_percentage": Decimal128("5.00"),
            "min_size": 2
        })

    if "rodzinny" not in existing_names:
        group_types.append({
            "name": "rodzinny",
            "discount_percentage": Decimal128("10.00"),
            "min_size": 3
        })

    if "grupowy" not in existing_names:
        group_types.append({
            "name": "grupowy",
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

if __name__=="__main__": 
    db.ticket_type.delete_many({})
    db.discount.delete_many({})
    db.group_type.delete_many({})
    db.special_offer.delete_many({})
    db.product.delete_many({})
    db.cinema.delete_many({})

    SPECIAL_OFFER_NUMBER = 10000
    PRODUCT_NUMBER = 10000
    CINEMA_NUMBER = 5000
    MAX_ROOM_NUMBER = 30
    MAX_SEAT_NUMBER = 100

    seed_ticket_type()
    seed_discount()
    seed_group_type()
    seed_special_offer(SPECIAL_OFFER_NUMBER)
    seed_product(PRODUCT_NUMBER)
    seed_cinema(cinema_count=CINEMA_NUMBER, max_room_count=MAX_ROOM_NUMBER, max_seat_count=MAX_SEAT_NUMBER)