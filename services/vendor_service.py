from database.connection import get_connection


def get_next_vendor(company_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM vendors
        WHERE company_id = %s
        AND active = 1
        ORDER BY
            CASE
                WHEN last_assigned IS NULL THEN 0
                ELSE 1
            END,
            last_assigned ASC
        LIMIT 1
    """, (company_id,))

    vendor = cursor.fetchone()

    # Consumir cualquier resultado pendiente
    cursor.fetchall()

    if vendor:

        cursor.execute("""
            UPDATE vendors
            SET last_assigned = NOW()
            WHERE id = %s
        """, (vendor["id"],))

        conn.commit()

    cursor.close()
    conn.close()

    return vendor