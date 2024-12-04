"""
Create fake data in the postgresql db.
It would be usefull to emulatie a transactional db as a data source
in a Data Enginneering ETL applicative db -> lakehouse
"""

import psycopg2

connection = psycopg2.connect(
    host="localhost", database="postgres", user="postgres", password="postgres"
)
cursor = connection.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    )
"""
)
connection.commit()
cursor.execute(
    """
    INSERT INTO users (name, email)
    VALUES (%s, %s)
""",
    ("John Doe", "john.doe@example.com"),
)
connection.commit()
cursor.execute("SELECT email FROM users WHERE name = %s", ("John Doe",))
user_email = cursor.fetchone()[0]
print(user_email)
