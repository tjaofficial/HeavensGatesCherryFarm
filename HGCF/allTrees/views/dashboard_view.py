from django.shortcuts import render # type: ignore
from ..models import individualTrees_model, locationTree_model, areaTree_model
from django.contrib.auth.decorators import login_required # type: ignore
# import paho.mqtt.client as mqtt
# from .mqtt_pub import on_connect, on_message, on_exit
# import atexit
import paho.mqtt.client as paho # type: ignore
from paho import mqtt # type: ignore

lock = login_required(login_url='Login')

@lock
def dashboard_view(request):
    treeData = individualTrees_model.objects.all()
    locationData = locationTree_model.objects.filter(locationID=1)
    areaData = areaTree_model.objects.all()
    noFooter = True
    smallHeader = True
    sideBar = True
    
    # setting callbacks for different events to see if it works, print the message etc.
    def on_connect(client, userdata, flags, rc, properties=None):
        print("CONNACK received with code %s." % rc)

    # with this callback you can see if your publish was successful
    def on_publish(client, userdata, mid, properties=None):
        print("mid: " + str(mid))

    # print which topic was subscribed to
    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    # print message, useful for checking if it was successful
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
    # userdata is user defined data of any type, updated by user_data_set()
    # client_id is the given name of the client
    client = paho.Client(client_id="HGCF_mqtt", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set("tjaofficial", "Tmattar1992!")
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect("9a39b7a6a28349a0849650ac1624b36e.s2.eu.hivemq.cloud", 8883)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish

    # subscribe to all topics of encyclopedia by using the wildcard "#"
    client.subscribe("encyclopedia/#", qos=1)

    # a single publish, this can also be done in loops, etc.
    client.publish("encyclopedia/temperature", payload="hot", qos=1)

    # loop_forever for simplicity, here you need to stop the loop manually
    # you can also use loop_start and loop_stop
    client.loop_start()
    client.loop_stop()
    
    
    return render(request, 'dashboard.html', {
        'teeData': treeData, 
        'noFooter': noFooter, 
        'smallHeader': smallHeader,
        'sideBar': sideBar,
        'locationData': locationData,
        'areaData': areaData,
    })