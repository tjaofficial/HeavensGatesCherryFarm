import requests # type: ignore
from .models import individualTrees_model, treeLogs_model, logCategory_model
import paho.mqtt.client as mqtt # type: ignore
import ssl
import json
import time
from django.utils.timezone import localtime
from django.conf import settings # type: ignore
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

alphabetKey = {'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5', 'f': '6', 'g': '7', 'h': '8', 'i': '9', 'j': '10', 'k': '11', 'l': '12', 'm': '13', 'n': '14', 'o': '15', 'p': '16', 'q': '17', 'r': '18', 's': '19', 't': '20', 'u': '21', 'v': '22', 'w': '23', 'x': '24', 'y': '25', 'z': '26', 'A': '27', 'B': '28', 'C': '29', 'D': '30', 'E': '31', 'F': '32', 'G': '33', 'H': '34', 'I': '35', 'J': '36', 'K': '37', 'L': '38', 'M': '39', 'N': '40', 'O': '41', 'P': '42', 'Q': '43', 'R': '44', 'S': '45', 'T': '46', 'U': '47', 'V': '48', 'W': '49', 'X': '50', 'Y': '51', 'Z': '52'}


def selectNextID(data, selector):
    newID = False
    if data.exists():
        print("DATA DOES EXISTS")
        if selector == "location":
            lastID = data[0].locationID[1:]# + 1
            starter = "L"
        elif selector == "area":
            lastID = int(data[0].areaID[1:]) + 1
            starter = "A"
        elif selector == "tree":
            lastID = data[0].treeID #+ 1
        lastIDLen = len(str(lastID))
        additionalZeros = 3 - lastIDLen
        newID = f"{starter}"
        for x in range(additionalZeros):
            newID += '0'
        newID += str(lastID)
        print(newID)
    else:
        newID = "001"
    return newID

def weatherDict(city):
    # request the API data and convert the JSON to Python data types
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=435ac45f81f3f8d42d164add25764f3c'
    try:
        city_weather = requests.get(url.format(city)).json()
        weather = {
            'city': city,
            'temperature': round(city_weather['main']['temp'], 0),
            'description': city_weather['weather'][0]['description'],
            'icon': city_weather['weather'][0]['icon'],
            'wind_speed': round(city_weather['wind']['speed'], 0),
            'wind_direction': city_weather['wind']['deg'],
            'humidity': city_weather['main']['humidity'],
        }
        degree = weather['wind_direction']
        
        def toTextualDescription(degree):
            if degree > 337.5:
                return 'N'
            if degree > 292.5:
                return 'NW'
            if degree > 247.5:
                return 'W'
            if degree > 202.5:
                return 'SW'
            if degree > 157.5:
                return 'S'
            if degree > 122.5:
                return 'SE'
            if degree > 67.5:
                return 'E'
            if degree > 22.5:
                return 'NE'
            return 'N'
        wind_direction = toTextualDescription(degree)
        weather['wind_direction'] = wind_direction
    except:
        weather = {
            'error': "Please inform Supervisor '" + str(city) + "' is not a valid city.",
            'city': False
        }
    return weather

def publish_valve_command(device_id: str, turn_on: bool):
    topic = f"shellyplus1-{device_id}/rpc"
    payload = {
        "id": 1,
        "src": "dashboard",  # This must match the subscription topic you're listening to!
        "method": "Switch.Set",
        "params": {
            "id": 0,
            "on": turn_on
        }
    }

    print(f"Publishing to {topic}: {json.dumps(payload)}")

    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
    client.loop_start()

    client.publish(topic, json.dumps(payload))
    time.sleep(0.5)  # give it a moment to publish
    client.loop_stop()
    client.disconnect()

def get_irrigation_log_messages(category, action, valve, user):
    templates = {
        'manual': {
            'start': f'✅ Manual override: Valve {valve.name} OPENED by {user.username if user else False} (Area {valve.areaID.name})',
            'stop': f'⏹️ Manual override: Valve {valve.name} CLOSED by {user.username if user else False} (Area {valve.areaID.name})',
        },
        'schedule': {
            'start': f'🔁✅ Scheduled watering STARTED for Area {valve.areaID.name} (Valve {valve.name})',
            'stop': f'🔁⏹️ Scheduled watering STOPPED for Area {valve.areaID.name} (Valve {valve.name})',
        },
        'emergency': {
            'stop_all': f'⚠️ EMERGENCY STOP: All valves closed by {user.username if user else False}'
        }
    }
    
    return templates[category][action]

def add_log_to_area_trees(valve, message, category):
    treeQuery = individualTrees_model.objects.filter(areaID=valve.areaID)
    for tree in treeQuery:
        newTreeLog = treeLogs_model(
            treeID=tree,
            timestamp=localtime(),
            note=message,
            category=logCategory_model.objects.get(name=category),
        )
        newTreeLog.save()

def build_seo(
    request,
    title,
    description,
    keywords=None,
    canonical=None,
    og_image=None,
    robots="index, follow"
):
    return {
        "seo_title": title,
        "seo_description": description,
        "seo_keywords": keywords or "",
        "seo_canonical": canonical or request.build_absolute_uri(),
        "og_title": title,
        "og_description": description,
        "og_url": canonical or request.build_absolute_uri(),
        "og_image": og_image or f"{request.scheme}://{request.get_host()}/static/images/HGCF-logo.png",
        "twitter_title": title,
        "twitter_description": description,
        "twitter_image": og_image or f"{request.scheme}://{request.get_host()}/static/images/HGCF-logo.png",
        "seo_robots": robots,
    }

def send_upick_reservation_confirmation(reservation):
    if not reservation.email:
        print(f"U-Pick email skipped: reservation {reservation.id} has no email.")
        return 0

    event = reservation.time_slot.event
    slot = reservation.time_slot

    event_date = event.date.strftime("%A, %B %d, %Y")
    slot_label = slot.get_slot_label()

    subject = f"Your {event.crop_name} U-Pick Reservation is Confirmed"

    context = {
        "reservation": reservation,
        "event": event,
        "slot": slot,
        "event_date": event_date,
        "slot_label": slot_label,
    }

    text_body = render_to_string(
        "emails/upick_reservation_confirmation.txt",
        context
    )

    html_body = render_to_string(
        "emails/upick_reservation_confirmation.html",
        context
    )

    print(f"Sending U-Pick confirmation email to {reservation.email} for reservation {reservation.id}")

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reservation.email],
    )

    email.attach_alternative(html_body, "text/html")

    return email.send(fail_silently=False)

def send_pos_receipt_email(sale, recipient_email=None, force=False):
    email_to = (recipient_email or sale.customer_email or "").strip().lower()

    if not email_to:
        print(f"POS receipt skipped: sale {sale.id} has no customer email.")
        return 0

    if sale.receipt_email_sent_at and not force:
        print(f"POS receipt skipped: sale {sale.id} receipt already sent.")
        return 0

    items = sale.items.select_related("product").all()

    subject = f"Your Heaven's Gates Cherry Farm Receipt - {sale.sale_number}"

    if force:
        subject = f"Receipt Copy - {sale.sale_number} - Heaven's Gates Cherry Farm"

    context = {
        "sale": sale,
        "items": items,
    }

    text_body = render_to_string("emails/pos_receipt.txt", context)
    html_body = render_to_string("emails/pos_receipt.html", context)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_to],
        )
        email.attach_alternative(html_body, "text/html")

        sent = email.send(fail_silently=False)

        sale.receipt_email_sent_at = timezone.now()
        sale.receipt_email_last_error = ""
        sale.save(update_fields=["receipt_email_sent_at", "receipt_email_last_error"])

        print(f"POS receipt sent to {email_to} for sale {sale.id}")

        return sent

    except Exception as exc:
        sale.receipt_email_last_error = str(exc)[:1000]
        sale.save(update_fields=["receipt_email_last_error"])

        print(f"POS receipt failed for sale {sale.id}: {exc}")

        raise