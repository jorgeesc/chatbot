from database.connection import get_connection


def create_lead(
    phone,
    customer_name,
    email,
    city,
    company_name,
    budget,
    comments,
    company_id,
    service_id,
    vendor_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads
        (
            phone,
            customer_name,
            email,
            city,
            company_name,
            budget,
            comments,
            company_id,
            service_id,
            vendor_id
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        phone,
        customer_name,
        email,
        city,
        company_name,
        budget,
        comments,
        company_id,
        service_id,
        vendor_id
    ))

    conn.commit()
    
    lead_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return lead_id