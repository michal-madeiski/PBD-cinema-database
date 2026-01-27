from datetime import timedelta
import random
from bson import Decimal128, ObjectId
from pymongo import MongoClient
from faker import Faker
from datetime import datetime

#CONFIG 
fake = Faker(['pl_PL']) 
client = MongoClient("mongodb://localhost:27017/")
db = client["moja-baza-mongo"]


def get_versions_pool(pool_size):
    """Generuje pulę unikalnych wersji do losowania"""
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

#CONST COLLECTIONS
VERSIONS = get_versions_pool(10)

#Helpery
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
def movies_and_screenings_sector(movies_count=1000, screenings_count =100000):    
    versions_pool = VERSIONS
    
    movies_batch = []
    screenings_archive_batch = []
    screenings_active_batch = []
    #FILMY
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

    #SCREENINGI
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
    

    ##Zapis
    if movies_batch:
        db.movie.insert_many(movies_batch)
        print(f"Dodano {len(movies_batch)} filmów.")
        
    if screenings_active_batch:
        db.screening.insert_many(screenings_active_batch)
        print(f"Dodano {len(screenings_active_batch)} AKTYWNYCH seansów.")

    if screenings_archive_batch:
        db.screening_archive.insert_many(screenings_archive_batch)
        print(f"Dodano {len(screenings_archive_batch)} ARCHIWALNYCH seansów.")

if __name__ == "__main__":
    print("Start seedowania")
    movies_and_screenings_sector(movies_count=1000, screenings_count=100_000) 