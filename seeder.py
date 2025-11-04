from db.connection import SessionLocal
from db.models import Movie, Version, License, Cinema, MovieVersion, Region, t_cinema_movie, Room 
from faker import Faker
import random


faker= Faker()


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



if __name__ == "__main__":
    print("Zaczynam seedowanie")


