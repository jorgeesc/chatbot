import requests

TOKEN = "EAAMYPxJFu7cBRy3OTlsMQTvZB1DwuGGoeTnLJZARl1pD8dDJOdenvLHFqrgqQXxZC3BFlU9SiAUKGZA1dIRrSFusuYHZAI49eiymtuf1FNQRP63QyIn1ShAqy2c1fczyznkvP9fPJCcmm6wj5jK23hcvHEsV8ZB6sk7aPrUyn50xNEIN4ELbz1nTZC1YrUzhkQM0AZBQjhQTuYPf26H5si81ZCO4uo8Ik1apPpWERMORTxhl12dh3ZCWHShUSWbEZBtW0HQRTJE7lSneuukF8yUYrvkgSn2w6TgGHaS6wZDZD"

PHONE_NUMBER_ID = "1074228509117424"


def send_message(phone, text):

    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.status_code)
    print(response.text)


def send_buttons(phone, body_text):

    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn1",
                            "title": "CLASIFIRAPIDOS"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn2",
                            "title": "MAIMEX"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btn3",
                            "title": "TVMOS"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.status_code)
    print(response.text)

def send_list(phone, body_text, rows):

    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": body_text
            },
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Empresas",
                        "rows": rows
                    }
                ]
            }
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.status_code)
    print(response.text)