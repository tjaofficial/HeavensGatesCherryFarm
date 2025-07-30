import paho.mqtt.client as mqtt # type: ignore
import ssl
import time
import json
from ..models import valve_registration
from django.conf import settings # type: ignore

# This will hold the status results keyed by device ID
valve_status_map = {}

# Device IDs to monitor
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        #print("✅ Connected to MQTT broker")
        client.subscribe("dashboard/rpc")
    else:
        print("❌ Failed to connect:", rc)

def on_message(client, userdata, msg):
    try:
        #print(f"📩 Message received on topic: {msg.topic}")
        payload = json.loads(msg.payload.decode())

        # Validate it's a response with result
        if "src" in payload and "result" in payload:
            device_id = payload["src"].replace("shellyplus1-", "")
            output = payload["result"].get("output", None)
            if output is not None:
                valve_status_map[device_id] = output
                #print(f"✅ [{device_id}] Output status: {output}")
    except Exception as e:
        print(f"❌ Error in on_message: {e}")

def get_valve_statuses():
    global has_primed_valves
    valve_status_map.clear()

    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
    client.loop_start()

    # Actively request each device's status
    for valve in valve_registration.objects.all():
        topic = f"shellyplus1-{valve.valveIP}/rpc"
        payload = json.dumps({
            "id": 1,
            "src": "dashboard",
            "method": "Switch.GetStatus",
            "params": {"id": 0}
        })
        client.publish(topic, payload)
        #print(f"Published status request to {topic}")

    time.sleep(2.5)  # Wait for responses

    if not valve_status_map:
        print("No statuses found. Sending OFF commands to prime MQTT topics...")
        for valve in valve_registration.objects.all():
            topic = f"shellyplus1-{valve.valveIP}/rpc"
            client.publish(topic, payload)
        has_primed_valves = True
        time.sleep(1.0)

    client.loop_stop()
    client.disconnect()

    return valve_status_map