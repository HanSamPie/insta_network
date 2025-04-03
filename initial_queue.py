import csv
import psycopg2

# Database connection settings
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432",
}

def add_item(name: str, status: str):
    """Inserts an item if it does not already exist."""
    query = """
    INSERT INTO tasks (name, status) VALUES (%s, %s)
    ON CONFLICT (name) DO NOTHING;
    """
    
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (name, status))
            conn.commit()

# BEFORE THIS DELETE ALL TROLL MANUALLY
with open("./form_responses.csv") as file:
    data = list(csv.DictReader(file))

users = [profile['Instagram Username'] for profile in data]

for user in users:
    add_item(user, "TODO")
