from database import get_connection


with get_connection() as connection:
    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT DISTINCT subject, property
            FROM facts
            ORDER BY subject, property;
            """
        )

        rows = cursor.fetchall()


for subject, property_name in rows:
    print(f"Subject: {subject}")
    print(f"Property: {property_name}")
    print()