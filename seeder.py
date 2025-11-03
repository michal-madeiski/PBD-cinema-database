from db.connection import SessionLocal
from db.models import Movie
from faker import Faker 


faker= Faker()

def seed_movies(n):
    session = SessionLocal()
    try: 
        movies= (Movie(title=faker.word(), director=faker.name(), duration_minutes=faker.random_int(min=60, max=200)) for i in range(n))
        session.add_all(movies)
        session.commit()
        print(f"Dodano {n} filmów do bazy danych!")
    except Exception as e:
        session.rollback()
        print("Błąd podczas seedowania:", e)
    finally: 
        session.close()



    
if __name__ == "__main__":
    print("Zaczynam seedowanie")
    seed_movies(300)
