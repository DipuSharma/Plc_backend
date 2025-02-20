import paho.mqtt.client as mqtt
from src.config.mongo_db import message_collection
from src.config.settings import setting
from src.app.plc_module.tasks import process_plc_message


# MQTT on connect
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker: {setting.MQTT_BROKER}")
    client.subscribe(setting.MQTT_TOPIC)

# MQTT on message received
def on_message(client, userdata, msg):
    payload = msg.payload.decode()  
    plc_id = msg.topic.split("/")[-1]

    # Store in MongoDB
    message_data = {"plc_id": plc_id, "message": payload}
    message_collection.insert_one(message_data)

    # Process with Celery
    process_plc_message.delay(plc_id, payload)

    print(f"Received from {msg.topic}: {payload}")

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(setting.MQTT_BROKER, setting.MQTT_PORT, 60)

def start_mqtt():
    mqtt_client.loop_start()
