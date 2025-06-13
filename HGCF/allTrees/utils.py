import requests # type: ignore
import paho.mqtt.client as mqtt # type: ignore
import ssl
import json
import time
from django.conf import settings # type: ignore

alphabetKey = {'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5', 'f': '6', 'g': '7', 'h': '8', 'i': '9', 'j': '10', 'k': '11', 'l': '12', 'm': '13', 'n': '14', 'o': '15', 'p': '16', 'q': '17', 'r': '18', 's': '19', 't': '20', 'u': '21', 'v': '22', 'w': '23', 'x': '24', 'y': '25', 'z': '26', 'A': '27', 'B': '28', 'C': '29', 'D': '30', 'E': '31', 'F': '32', 'G': '33', 'H': '34', 'I': '35', 'J': '36', 'K': '37', 'L': '38', 'M': '39', 'N': '40', 'O': '41', 'P': '42', 'Q': '43', 'R': '44', 'S': '45', 'T': '46', 'U': '47', 'V': '48', 'W': '49', 'X': '50', 'Y': '51', 'Z': '52'}


def selectNextID(data, selector):
    newID = False
    if data.exists():
        print("DATA DOES EXISTS")
        if selector == "location":
            lastID = data[0].locationID# + 1
        elif selector == "area":
            lastID = data[0].areaID #+ 1
        elif selector == "tree":
            lastID = data[0].treeID #+ 1
        lastIDLen = len(str(lastID))
        additionalZeros = 3 - lastIDLen
        newID = ''
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


