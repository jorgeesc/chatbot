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
    update_step,
    reset_session
)

from urllib.parse import quote

import os
from dotenv import load_dotenv


load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# ==========================================================
# VERIFICACIÓN DEL WEBHOOK
# ==========================================================

@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "Error", 403


# ==========================================================
# RECEPCIÓN DE MENSAJES
# ==========================================================

@app.route("/webhook", methods=["POST"])
def receive():

    data = request.json

    try:

        value = data["entry"][0]["changes"][0]["value"]

        # Ignorar eventos que no contienen mensajes
        if "messages" not in value:
            return "ok", 200

        message_data = value["messages"][0]

        phone = message_data["from"]

        print("===================================")
        print(message_data)
        print("===================================")

        # ==================================================
        # MENSAJES DE TEXTO
        # ==================================================

        if message_data["type"] == "text":

            text = message_data["text"]["body"].strip()

            session = get_session(phone)

            # ==================================================
            # PRIMERA VEZ
            # ==================================================

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

            # ==================================================
            # NOMBRE
            # ==================================================

            if current_step == "name":

                update_customer_name(phone, text)

                send_message(
                    phone,
                    """📧 ¿Cuál es tu correo electrónico?

Si no deseas compartirlo escribe NO"""
                )

                return "ok", 200

            # ==================================================
            # EMAIL
            # ==================================================

            elif current_step == "email":

                update_email(phone, text)

                send_message(
                    phone,
                    "📍 ¿De qué ciudad nos contactas?"
                )

                return "ok", 200

            # ==================================================
            # CIUDAD
            # ==================================================

            elif current_step == "city":

                update_city(phone, text)

                update_step(phone, "company_name")

                send_message(
                    phone,
                    """🏢 ¿Cuál es el nombre de tu empresa o negocio?

Si aún no tienes una empresa escribe:
PARTICULAR"""
                )

                return "ok", 200

            # ==================================================
            # NOMBRE DE LA EMPRESA DEL CLIENTE
            # ==================================================

            elif current_step == "company_name":

                update_company_name(phone, text)

                send_message(
                    phone,
                    """💰 ¿Cuál es tu presupuesto aproximado?

Escribe únicamente el número de una opción:

1️⃣ Menos de $5,000

2️⃣ $5,000 - $20,000

3️⃣ $20,000 - $50,000

4️⃣ Más de $50,000"""
                )

                return "ok", 200

            # ==================================================
            # PRESUPUESTO
            # ==================================================

            elif current_step == "budget":

                budget_options = {
                    "1": "Menos de $5,000",
                    "2": "$5,000 - $20,000",
                    "3": "$20,000 - $50,000",
                    "4": "Más de $50,000"
                }

                # Validar que únicamente escriba 1, 2, 3 o 4
                if text not in budget_options:

                    send_message(
                        phone,
                        """⚠️ Opción de presupuesto no válida.

Por favor escribe únicamente el número de una opción:

1️⃣ Menos de $5,000

2️⃣ $5,000 - $20,000

3️⃣ $20,000 - $50,000

4️⃣ Más de $50,000"""
                    )

                    # No avanzamos de etapa
                    return "ok", 200

                # Convertir la opción en el rango real
                budget = budget_options[text]

                update_budget(phone, budget)

                send_message(
                    phone,
                    """✍️ Describe brevemente lo que necesitas.

Ejemplo:

Necesito promocionar una vacante.

o

Quiero cotizar una campaña publicitaria."""
                )

                return "ok", 200

            # ==================================================
            # COMENTARIOS / FINALIZAR LEAD
            # ==================================================

            elif current_step == "comments":

                update_comments(phone, text)

                # Recuperar nuevamente la sesión actualizada
                session = get_session(phone)

                company_id = session["company_id"]
                service_id = session["service_id"]

                # ==================================================
                # ASIGNAR VENDEDOR
                # ==================================================

                vendor = get_next_vendor(company_id)

                if not vendor:

                    print(
                        f"No existen vendedores activos "
                        f"para company_id={company_id}"
                    )

                    send_message(
                        phone,
                        """⚠️ Tu solicitud fue recibida, pero en este momento no pudimos asignar un asesor.

Nuestro equipo dará seguimiento a tu solicitud."""
                    )

                    reset_session(phone)

                    return "ok", 200

                # ==================================================
                # CREAR LEAD
                # ==================================================

                lead_id = create_lead(
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

                # ==================================================
                # RESPONDER AL CLIENTE
                # ==================================================

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

                # ==================================================
                # CREAR ENLACE PARA QUE EL VENDEDOR CONTACTE AL CLIENTE
                # ==================================================

                mensaje_seguimiento = (
                    f"Hola {session['customer_name']}, "
                    f"soy {vendor['name']} y daré seguimiento "
                    f"a tu solicitud."
                )

                mensaje_codificado = quote(mensaje_seguimiento)

                enlace_whatsapp = (
                    f"https://wa.me/{phone}"
                    f"?text={mensaje_codificado}"
                )

                # ==================================================
                # MENSAJE PARA EL VENDEDOR
                # ==================================================

                mensaje_vendedor = f"""🔔 NUEVO LEAD ASIGNADO

🆔 Lead:
{lead_id}

🏢 Empresa o negocio:
{session['company_name']}

👤 Cliente:
{session['customer_name']}

📱 Teléfono:
{phone}

💬 Contactar al cliente:
{enlace_whatsapp}

📧 Correo:
{session['email']}

📍 Ciudad:
{session['city']}

💰 Presupuesto:
{session['budget']}

✍️ Comentarios:
{text}

El cliente fue asignado a ti para seguimiento."""

                # ==================================================
                # NOTIFICAR AL VENDEDOR
                # ==================================================

                try:

                    send_message(
                        vendor["phone"],
                        mensaje_vendedor
                    )

                    print(
                        f"Notificación enviada al vendedor "
                        f"{vendor['name']} - Lead {lead_id}"
                    )

                except Exception as error:

                    print(
                        f"Error notificando al vendedor "
                        f"{vendor['name']}: {error}"
                    )

                # ==================================================
                # FINALIZAR SESIÓN
                # ==================================================

                reset_session(phone)

                return "ok", 200

            # ==================================================
            # ESTADO NO RECONOCIDO
            # ==================================================

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

        # ==================================================
        # MENSAJES INTERACTIVOS
        # ==================================================

        elif message_data["type"] == "interactive":

            selected_id = message_data[
                "interactive"
            ]["list_reply"]["id"]

            selected_title = message_data[
                "interactive"
            ]["list_reply"]["title"]

            print("ID:", selected_id)
            print("TITLE:", selected_title)

            # ==================================================
            # EMPRESA
            # ==================================================

            if selected_id.startswith("company_"):

                company_id = int(
                    selected_id.replace(
                        "company_",
                        ""
                    )
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
                    f"Seleccionaste {selected_title}\n\n"
                    "Seleccione un servicio",
                    rows
                )

            # ==================================================
            # SERVICIO
            # ==================================================

            elif selected_id.startswith("service_"):

                service_id = int(
                    selected_id.replace(
                        "service_",
                        ""
                    )
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

    except Exception as error:

        import traceback

        print(
            f"Error procesando webhook: {error}"
        )

        traceback.print_exc()

        return "ok", 200