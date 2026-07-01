from database.connection import get_connection


def get_services_by_company(company_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name
        FROM services
        WHERE company_id = %s
        AND active = 1
        ORDER BY name
    """, (company_id,))

    services = cursor.fetchall()

    cursor.close()
    conn.close()

    return services

def get_service_by_id(service_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM services
        WHERE id = %s
    """, (service_id,))

    service = cursor.fetchone()

    cursor.close()
    conn.close()

    return service