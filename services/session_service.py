from database.connection import get_connection


def get_session(phone):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM sessions WHERE phone = %s",
        (phone,)
    )

    session = cursor.fetchone()

    cursor.close()
    conn.close()

    return session


def create_session(phone):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO sessions
        (phone, current_step)
        VALUES (%s, %s)
        """,
        (phone, "empresa")
    )

    conn.commit()

    cursor.close()
    conn.close()


def update_step(phone, step):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE sessions
        SET current_step=%s
        WHERE phone=%s
        """,
        (step, phone)
    )

    conn.commit()

    cursor.close()
    conn.close()
    
def update_company(phone, company_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET company_id=%s,
            current_step='service'
        WHERE phone=%s
    """, (company_id, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def update_service(phone, service_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET service_id=%s,
            current_step='name'
        WHERE phone=%s
    """, (service_id, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def update_customer_name(phone, customer_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET customer_name=%s,
            current_step='email'
        WHERE phone=%s
    """, (customer_name, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def update_email(phone, email):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET email=%s,
            current_step='city'
        WHERE phone=%s
    """, (email, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def update_city(phone, city):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET city=%s,
            current_step='completed'
        WHERE phone=%s
    """, (city, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def update_company_name(phone, company_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET company_name=%s,
            current_step='budget'
        WHERE phone=%s
    """, (company_name, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def update_budget(phone, budget):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET budget=%s,
            current_step='comments'
        WHERE phone=%s
    """, (budget, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def update_comments(phone, comments):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET comments=%s,
            current_step='completed'
        WHERE phone=%s
    """, (comments, phone))

    conn.commit()

    cursor.close()
    conn.close()
    
def reset_session(phone):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET
            current_step='empresa',
            company_id=NULL,
            service_id=NULL,
            customer_name=NULL,
            email=NULL,
            city=NULL,
            company_name=NULL,
            budget=NULL,
            comments=NULL
        WHERE phone=%s
    """, (phone,))

    conn.commit()

    cursor.close()
    conn.close()