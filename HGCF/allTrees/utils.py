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
from datetime import datetime
from django.core.cache import cache

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

# Weather

HALE_LAT = 44.377972
HALE_LON = -83.8047965

NWS_HEADERS = {
    "User-Agent": "HeavensGatesCherryFarm.com, contact@heavensgatescherryfarm.com",
    "Accept": "application/geo+json",
}


def get_hale_nws_forecast():
    """
    Gets a detailed forecast for Hale, MI using the National Weather Service API.
    No API key required.
    """

    try:
        # Step 1: Convert lat/lon to NWS grid forecast URLs
        point_url = f"https://api.weather.gov/points/{HALE_LAT},{HALE_LON}"
        point_response = requests.get(point_url, headers=NWS_HEADERS, timeout=10)
        point_response.raise_for_status()

        point_data = point_response.json()
        forecast_url = point_data["properties"]["forecast"]
        hourly_url = point_data["properties"]["forecastHourly"]

        # Step 2: Get 7-day forecast periods
        forecast_response = requests.get(forecast_url, headers=NWS_HEADERS, timeout=10)
        forecast_response.raise_for_status()

        forecast_data = forecast_response.json()
        periods = forecast_data["properties"]["periods"]

        forecast_periods = []

        for period in periods:
            forecast_periods.append({
                "name": period.get("name"),
                "start_time": period.get("startTime"),
                "end_time": period.get("endTime"),
                "is_daytime": period.get("isDaytime"),
                "temperature": period.get("temperature"),
                "temperature_unit": period.get("temperatureUnit"),
                "wind_speed": period.get("windSpeed"),
                "wind_direction": period.get("windDirection"),
                "short_forecast": period.get("shortForecast"),
                "detailed_forecast": period.get("detailedForecast"),
                "icon": period.get("icon"),
            })

        return {
            "success": True,
            "city": "Hale",
            "state": "MI",
            "source": "National Weather Service",
            "updated_at": datetime.now().strftime("%B %d, %Y at %-I:%M %p"),
            "periods": forecast_periods,
            "hourly_url": hourly_url,
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "message": "Weather data could not be loaded right now.",
            "error": str(e),
            "periods": [],
        }
    except KeyError as e:
        return {
            "success": False,
            "message": "Weather data came back in an unexpected format.",
            "error": str(e),
            "periods": [],
        }

def get_cached_hale_forecast():
    cache_key = "hale_nws_forecast"
    weather = cache.get(cache_key)

    if weather:
        return weather

    weather = get_hale_nws_forecast()
    cache.set(cache_key, weather, 60 * 20)  # cache for 20 minutes

    return weather


HALE_LAT = 44.377972
HALE_LON = -83.8047965


WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Heavy thunderstorm with hail",
}


def get_weather_description(code):
    return WEATHER_CODE_MAP.get(code, "Unknown")


def get_frost_risk(low_temp, rain_sum, wind_speed):
    """
    Simple farm-focused frost risk.
    This is not a scientific frost model, but it is useful as a warning layer.
    """

    if low_temp is None:
        return {
            "level": "unknown",
            "label": "Unknown",
            "message": "Not enough data to calculate frost risk.",
        }

    if low_temp <= 32:
        return {
            "level": "high",
            "label": "High Frost Risk",
            "message": "Low temperature is at or below freezing. Protect sensitive crops if needed.",
        }

    if low_temp <= 36 and rain_sum < 0.05 and wind_speed <= 8:
        return {
            "level": "medium",
            "label": "Possible Frost Risk",
            "message": "Cold, calm, and dry conditions could allow frost in low spots.",
        }

    if low_temp <= 38:
        return {
            "level": "low",
            "label": "Low Frost Risk",
            "message": "Chilly overnight, but frost risk does not look major right now.",
        }

    return {
        "level": "none",
        "label": "No Frost Risk",
        "message": "Temperatures look safely above frost range.",
    }


def get_picking_condition(max_temp, rain_probability, rain_sum, wind_gusts, weather_code):
    """
    Creates a customer-friendly picking condition.
    """

    description = get_weather_description(weather_code)

    if rain_probability >= 70 or rain_sum >= 0.25:
        return {
            "level": "poor",
            "label": "Poor Picking Conditions",
            "message": "Rain is likely. Picking may be muddy or interrupted.",
        }

    if wind_gusts >= 30:
        return {
            "level": "caution",
            "label": "Windy Conditions",
            "message": "Strong gusts possible. Keep an eye on farm updates before coming out.",
        }

    if max_temp >= 88:
        return {
            "level": "caution",
            "label": "Hot Picking Conditions",
            "message": "It may be hot in the field. Bring water and come earlier if possible.",
        }

    if rain_probability >= 40:
        return {
            "level": "fair",
            "label": "Fair Picking Conditions",
            "message": "Some rain is possible, but the day may still be workable.",
        }

    if weather_code in [0, 1, 2, 3]:
        return {
            "level": "good",
            "label": "Good Picking Conditions",
            "message": f"{description}. Looks like a solid day for picking.",
        }

    return {
        "level": "fair",
        "label": "Fair Picking Conditions",
        "message": f"{description}. Check closer to arrival time.",
    }


def get_irrigation_note(rain_sum, evapotranspiration, max_temp):
    """
    Very simple irrigation suggestion.
    Later we can connect this to your actual valve schedule.
    """

    if rain_sum >= 0.5:
        return {
            "level": "skip",
            "label": "Likely Skip Irrigation",
            "message": "Rainfall may be enough to reduce or skip watering.",
        }

    if rain_sum >= 0.2:
        return {
            "level": "watch",
            "label": "Watch Soil Moisture",
            "message": "Some rain expected. Check soil before running irrigation.",
        }

    if evapotranspiration is not None and evapotranspiration >= 0.18:
        return {
            "level": "water",
            "label": "Irrigation Likely Needed",
            "message": "Drying conditions look higher. Soil may need water.",
        }

    if max_temp >= 86 and rain_sum < 0.1:
        return {
            "level": "water",
            "label": "Hot and Dry",
            "message": "Heat with little rain may dry beds faster.",
        }

    return {
        "level": "normal",
        "label": "Normal",
        "message": "No major irrigation warning from forecast data.",
    }


def get_hale_farm_weather():
    cache_key = "hale_open_meteo_farm_weather"
    cached_weather = cache.get(cache_key)

    if cached_weather:
        return cached_weather

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": HALE_LAT,
        "longitude": HALE_LON,
        "timezone": "America/Detroit",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "forecast_days": 7,
        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "uv_index_max",
            "sunrise",
            "sunset",
            "et0_fao_evapotranspiration",
        ]),
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        days = []

        dates = daily.get("time", [])

        for index, raw_date in enumerate(dates):
            weather_code = daily.get("weather_code", [None])[index]
            max_temp = daily.get("temperature_2m_max", [None])[index]
            min_temp = daily.get("temperature_2m_min", [None])[index]
            rain_sum = daily.get("precipitation_sum", [0])[index] or 0
            rain_probability = daily.get("precipitation_probability_max", [0])[index] or 0
            wind_speed = daily.get("wind_speed_10m_max", [0])[index] or 0
            wind_gusts = daily.get("wind_gusts_10m_max", [0])[index] or 0
            uv_index = daily.get("uv_index_max", [None])[index]
            sunrise = daily.get("sunrise", [None])[index]
            sunset = daily.get("sunset", [None])[index]
            evapotranspiration = daily.get("et0_fao_evapotranspiration", [None])[index]

            date_obj = datetime.strptime(raw_date, "%Y-%m-%d")

            frost_risk = get_frost_risk(
                low_temp=min_temp,
                rain_sum=rain_sum,
                wind_speed=wind_speed,
            )

            picking_condition = get_picking_condition(
                max_temp=max_temp,
                rain_probability=rain_probability,
                rain_sum=rain_sum,
                wind_gusts=wind_gusts,
                weather_code=weather_code,
            )

            irrigation_note = get_irrigation_note(
                rain_sum=rain_sum,
                evapotranspiration=evapotranspiration,
                max_temp=max_temp,
            )

            days.append({
                "date": raw_date,
                "day_name": date_obj.strftime("%A"),
                "display_date": date_obj.strftime("%b %-d"),
                "weather_code": weather_code,
                "description": get_weather_description(weather_code),
                "max_temp": round(max_temp) if max_temp is not None else None,
                "min_temp": round(min_temp) if min_temp is not None else None,
                "rain_sum": round(rain_sum, 2),
                "rain_probability": round(rain_probability),
                "wind_speed": round(wind_speed),
                "wind_gusts": round(wind_gusts),
                "uv_index": round(uv_index, 1) if uv_index is not None else None,
                "sunrise": sunrise,
                "sunset": sunset,
                "evapotranspiration": round(evapotranspiration, 2) if evapotranspiration is not None else None,
                "frost_risk": frost_risk,
                "picking_condition": picking_condition,
                "irrigation_note": irrigation_note,
            })

        farm_weather = {
            "success": True,
            "source": "Open-Meteo",
            "city": "Hale",
            "state": "MI",
            "updated_at": datetime.now().strftime("%B %d, %Y at %-I:%M %p"),
            "days": days,
        }

        cache.set(cache_key, farm_weather, 60 * 30)
        return farm_weather

    except requests.RequestException as e:
        return {
            "success": False,
            "message": "Farm weather data could not be loaded right now.",
            "error": str(e),
            "days": [],
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Something went wrong while processing farm weather data.",
            "error": str(e),
            "days": [],
        }
