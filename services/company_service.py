from database.connection import get_connection


def get_companies():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name
        FROM companies
        WHERE active = 1
        ORDER BY name
    """)

    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return companies