import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
db_url = os.getenv("DATABASE_URL")
try: 
    engine = create_engine(db_url, echo=False)
    with engine.connect() as conn:
        print("Poprawnie połaczono")
except Exception as e:
    print(f"Nie połączono: {e}")
