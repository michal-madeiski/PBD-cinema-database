import random
from pymongo import MongoClient, errors
from faker import Faker
from datetime import timedelta
from bson import ObjectId, Decimal128
import random

#CONFIG 
fake = Faker(['pl_PL']) 
client = MongoClient("mongodb://localhost:27017")
db = client["cinema_mongodb_local"]

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
            "price": product_for_snapshot["price"]*count,
        }
        product_snapshot_total_price += product_snapshot["price"]
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
            "dicsount_percentage": group_type_discount_percentage
        }

        seats_snapshot = []
        ticket_price = 0
        for i in range(ticket_seats_amount):
            actual_seat_number = taken_seats_from_screening[current_taken_seat_index + i]

            ticket_type_for_seat = random.choice(ticket_type_list)
            seat_price = ticket_type_for_seat["base_price"]
            seat_price_for_total = (1 - group_type_discount_percentage/100)*seat_price
            
            
            seat = {
                "seat_number": actual_seat_number,
                "ticket_type_id": ticket_type_for_seat["_id"],
                "ticket_name": ticket_type_for_seat["name"],
                "ticket_base_price": seat_price,
            }
            if random.random() >= 0.7:
                dicsount_for_seat = random.choice(discount_list)
                seat["discount_id"] = dicsount_for_seat["_id"]
                seat["discount_name"] = dicsount_for_seat["name"]
                seat["discount_percentage"] = dicsount_for_seat["percentage"]
                seat_price_for_total = (1 - dicsount_for_seat["percentage"]/100)*seat_price
            
            ticket_price += seat_price_for_total
            seats_snapshot.append(seat)

        special_offer_for_ticket = random.choice(special_offer_list)
        special_offer_id = special_offer_for_ticket["_id"]
        special_offer_amount = special_offer_for_ticket["amount"]

        special_offer_total_minus = special_offer_amount * ticket_seats_amount
        ticket_price -= special_offer_total_minus
        if ticket_price < 0:
            ticket_price = 0
        ticket = {
            "total_price": ticket_price,
            "qr_code": fake.uuid4(),
            "status": ticket_status,
            "group_type_snapshot": group_type_snapshot,
            "screening_id": screening_id,
            "movie_title": movie_title,
            "special_offer_id": special_offer_id,
            "special_offer_amount": special_offer_total_minus,
            "seats_snapshot": seats_snapshot
        }
        tickets_total_price += ticket_price
        ticket_list.append(ticket)
        current_seat_index += ticket_seats_amount
    return ticket_list, tickets_total_price

def seed_order(batch_size): 
    user_ids = [user["_id"] for user in db["user"].find({"type": "client"}, {"_id": 1})]
    cinema_ids = [cinema["_id"] for cinema in db["cinema"].find({}, {"_id": 1})]

    product_list = list(db["product"].find())

    group_type_list = list(db["group_type"].find())
    screening_list = list(db["screening"].find())
    screening_archive_list = list(db["screening_archive"].find())
    screening_with_flag = [(screening_archive_list, True), (screening_list, False)]
    special_offer_list = list(db["special_offer"].find())
    ticket_type_list = list(db["ticket_type"].find())
    discount_list = list(db["discount"].find())

    order_list = []

    for curr_screening_list, is_archive in screening_with_flag:
        for screening in curr_screening_list:
            screening_start_time = screening["start_time"]
            filtered_special_offer_list = [offer for offer in special_offer_list if offer["start_time"] < screening_start_time]
            taken_seats_numbers = [seat["seat_number"] for seat in screening["taken_seats"]]
            total_seats_amount = len(taken_seats_numbers)

            curr_idx = 0

            while curr_idx < total_seats_amount:
                order_amount = 0
                order_status = "paid" if is_archive else random.choices(["reserved", "pending", "paid"], weights=[4, 1, 95], k=1)[0]
                order_seats_amount = random.randint(1, 10)
                end_idx = min(curr_idx + order_seats_amount, total_seats_amount)

                seats_chunk_for_order = taken_seats_numbers[curr_idx : end_idx]

                tickets, tickets_total_price = ticket_for_order(
                    taken_seats_from_screening=seats_chunk_for_order,
                    screening_id=screening["id"],
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
                    order["payment_type"] = random.choice(["blik", "cash", "card", "online", "voucher"])

                    #PRODUCT_SNAPSHOT
                    product_snapshot_prob = random.random()
                    if product_snapshot_prob >= 0.7:
                        product_snapshot_list, product_snapshot_total_price = product_snapshot_for_order(product_list)
                        order_amount += product_snapshot_total_price
                        order["product_snapshot"] = product_snapshot_list
                    #PRODUCT_SNAPSHOT

                order["amount"] = order_amount

                order_list.append(order)
                curr_idx = end_idx

                if len(order_list) > batch_size:
                    try:
                        db["order"].insert_many(order_list)
                        order_list = []
                        print(f"Zapisano {batch_size} order")
                    except errors.BulkWriteError as bwe:
                        print("Błąd walidacji przy order!")
                        print(bwe.details['writeErrors'][0])
                    except Exception as e:
                        print(f"Inny błąd: {e}")
    if order_list:
        try:
            db["order"].insert_many(order_list)
            print(f"Zapisano {len(order_list)} order")
        except errors.BulkWriteError as bwe:
            print("Błąd walidacji przy order!")
            print(bwe.details['writeErrors'][0])
        except Exception as e:
            print(f"Inny błąd: {e}")



if __name__=="__main__": 
    pass