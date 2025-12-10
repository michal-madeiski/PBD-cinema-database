import os
import psycopg2
import csv

# CONFIG
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = "" 
DB_HOST = ""
QUERIES_DIR = ""
OUTPUT_DIR = ""
# CONFIG

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
cur = conn.cursor()

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in sorted(os.listdir(QUERIES_DIR)):
    if filename.startswith("q_") and filename.endswith(".sql"):
        sql_path = os.path.join(QUERIES_DIR, filename)

        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()

        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]

        csv_path = os.path.join(OUTPUT_DIR, filename.replace(".sql", ".csv"))

        with open(csv_path, "w", encoding="utf-8-sig", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(colnames)
            writer.writerows(rows)

        print(f"Wygenerowano: {csv_path}")

cur.close()
conn.close()