from flask import request
from app import app

from services.whatsapp_service import send_message, send_list
from services.company_service import get_companies
from services.service_service import get_services_by_company
from services.vendor_service import get_next_vendor
from services.lead_service import create_lead

from services.session_service import (
    get_session,
    create_session,
    update_company,
    update_service,
    update_customer_name,
    update_email,
    update_city,
    update_company_name,
    update_budget,
    update_comments,
    reset_session
)

VERIFY_TOKEN = "MiToken123"


@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "Error", 403


@app.route("/webhook", methods=["POST"])
def receive():

    data = request.json

    try:

        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "ok", 200

        message_data = value["messages"][0]

        phone = message_data["from"]

        print("===================================")
        print(message_data)
        print("===================================")

        # ==========================================
        # MENSAJES DE TEXTO
        # ==========================================

        if message_data["type"] == "text":

            text = message_data["text"]["body"].strip()

            session = get_session(phone)

            # Primera vez
            if not session:

                create_session(phone)

                companies = get_companies()

                rows = []

                for company in companies:

                    rows.append({
                        "id": f"company_{company['id']}",
                        "title": company["name"][:24]
                    })

                send_list(
                    phone,
                    "👋 Bienvenido\n\nSeleccione una empresa",
                    rows
                )

                return "ok", 200

            current_step = session["current_step"]

            # ==========================
            # NOMBRE
            # ==========================

            if current_step == "name":

                update_customer_name(phone, text)

                send_message(
                    phone,
                    "📧 ¿Cuál es tu correo electrónico?\n\nSi no deseas compartirlo escribe NO"
                )

                return "ok", 200

            # ==========================
            # EMAIL
            # ==========================

            elif current_step == "email":

                update_email(phone, text)

                send_message(
                    phone,
                    "📍 ¿De qué ciudad nos contactas?"
                )

                return "ok", 200

            # ==========================
            # CIUDAD
            # ==========================
            elif current_step == "city":

                update_city(phone, text)

                from services.session_service import update_step

                update_step(phone, "company_name")

                send_message(
                    phone,
                    """🏢 ¿Cuál es el nombre de tu empresa o negocio?

Si aún no tienes una empresa escribe:
PARTICULAR"""
                )

                return "ok", 200
            
            elif current_step == "company_name":

                update_company_name(phone, text)

                send_message(
                    phone,
                    """💰 ¿Cuál es tu presupuesto aproximado?

1️⃣ Menos de $5,000

2️⃣ $5,000 - $20,000

3️⃣ $20,000 - $50,000

4️⃣ Más de $50,000"""
                )

                return "ok", 200
            
            
            elif current_step == "budget":

                update_budget(phone, text)

                send_message(
                    phone,
                    """✍️ Describe brevemente lo que necesitas.

Ejemplo:

Necesito promocionar una vacante.

o

Quiero cotizar una campaña publicitaria."""
                )

                return "ok", 200 


            elif current_step == "comments":

                update_comments(phone, text)

                session = get_session(phone)

                company_id = session["company_id"]
                service_id = session["service_id"]

                vendor = get_next_vendor(company_id)

                create_lead(
                    phone,
                    session["customer_name"],
                    session["email"],
                    session["city"],
                    session["company_name"],
                    session["budget"],
                    text,
                    company_id,
                    service_id,
                    vendor["id"]
                )

                send_message(
                    phone,
                    f"""✅ Gracias {session['customer_name']}

Tu solicitud ha sido registrada correctamente.

👤 Asesor asignado:
{vendor['name']}

📱 WhatsApp:
{vendor['phone']}

https://wa.me/{vendor['phone']}

En breve se pondrá en contacto contigo."""
                )

                reset_session(phone)

                return "ok", 200
            # Si escribe cualquier cosa después
            else:

                companies = get_companies()

                rows = []

                for company in companies:

                    rows.append({
                        "id": f"company_{company['id']}",
                        "title": company["name"][:24]
                    })

                send_list(
                    phone,
                    "Seleccione una empresa",
                    rows
                )

                return "ok", 200

        # ==========================================
        # MENSAJES INTERACTIVOS
        # ==========================================

        elif message_data["type"] == "interactive":

            selected_id = message_data["interactive"]["list_reply"]["id"]
            selected_title = message_data["interactive"]["list_reply"]["title"]

            print("ID:", selected_id)
            print("TITLE:", selected_title)

            # ==========================
            # EMPRESA
            # ==========================

            if selected_id.startswith("company_"):

                company_id = int(
                    selected_id.replace("company_", "")
                )

                update_company(
                    phone,
                    company_id
                )

                services = get_services_by_company(
                    company_id
                )

                rows = []

                for service in services:

                    rows.append({
                        "id": f"service_{service['id']}",
                        "title": service["name"][:24]
                    })

                send_list(
                    phone,
                    f"Seleccionaste {selected_title}\n\nSeleccione un servicio",
                    rows
                )

            # ==========================
            # SERVICIO
            # ==========================

            elif selected_id.startswith("service_"):

                service_id = int(
                    selected_id.replace("service_", "")
                )

                update_service(
                    phone,
                    service_id
                )

                send_message(
                    phone,
                    f"""✅ Servicio seleccionado:

{selected_title}

👤 Antes de asignarte un asesor,

¿Cuál es tu nombre completo?"""
                )

        return "ok", 200

    except Exception as e:

        import traceback
        traceback.print_exc()

        return "ok", 200

