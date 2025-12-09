import os
import psycopg2
import csv

# --- USTAWIENIA ---
DB_NAME = "cinema_db"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"

QUERIES_DIR = "."          # folder z q_01.sql itd.
OUTPUT_DIR = "results"     # folder na CSV

# --- POŁĄCZENIE Z BAZĄ ---
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
cur = conn.cursor()

# --- TWORZENIE FOLDERU NA WYNIKI ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- ITERACJA PO PLIKACH SQL ---
for filename in sorted(os.listdir(QUERIES_DIR)):
    if filename.startswith("q_") and filename.endswith(".sql"):
        sql_path = os.path.join(QUERIES_DIR, filename)

        # wczytanie treści zapytania
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()

        # wykonanie kwerendy
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]

        # ścieżka pliku wyjściowego
        csv_path = os.path.join(OUTPUT_DIR, filename.replace(".sql", ".csv"))

        # zapis CSV z polskimi znakami
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(colnames)
            writer.writerows(rows)

        print(f"Wygenerowano: {csv_path}")

# zamknięcie połączenia
cur.close()
conn.close()
