import psycopg2

# Database connection settings
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432",
}

def create_table():
    """Creates the 'tasks' table in the PostgreSQL database."""
    create_table_query = """
    DROP TABLE tasks;
    CREATE TABLE IF NOT EXISTS tasks (
        name TEXT PRIMARY KEY,
        status TEXT CHECK (status IN ('DONE', 'TODO', 'ONGOING')),
        depth INT NOT NULL
    );
    """

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()
            print("Table 'tasks' created successfully (if it didn't exist).")

# Run the function
create_table()