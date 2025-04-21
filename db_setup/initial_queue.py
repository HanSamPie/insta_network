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

def add_profile_with_depth(name: str, status: str, depth: int):
    """Add a new task with a specified depth."""
    query = """
    INSERT INTO tasks (name, status, depth)
    VALUES (%s, %s, %s)
    ON CONFLICT (name) DO NOTHING;
    """

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (name, status, depth))
            conn.commit()

# BEFORE THIS DELETE ALL TROLL MANUALLY
with open("./form_responses.csv") as file:
    data = list(csv.DictReader(file))

users = [profile['Instagram Username'] for profile in data]

for user in users:
    add_profile_with_depth(user, "TODO", 0)
