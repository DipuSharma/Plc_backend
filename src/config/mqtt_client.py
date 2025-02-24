import paho.mqtt.client as mqtt
import time
import json
from src.config.mongo_db import message_collection
from src.config.settings import setting
from src.app.plc_module.tasks import process_plc_message

MQTT_BROKER = setting.MQTT_BROKER or "mqtt"
MQTT_PORT = int(setting.MQTT_PORT or 1883)
MQTT_TOPIC = setting.MQTT_TOPIC or "plc/"

# MQTT Connect Callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(f"{MQTT_TOPIC}#")  # Subscribe to all PLC topics
    else:
        print(f"❌ Failed to connect, return code {rc}")

# MQTT Message Callback
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        plc_id = msg.topic.split("/")[-1]

        # Store in MongoDB
        message_data = {"plc_id": plc_id, "message": payload}
        message_collection.insert_one(message_data)

        # Send message for background processing
        process_plc_message.delay(plc_id, payload)

        print(f"📩 Received from {msg.topic}: {payload}")

    except Exception as e:
        print(f"🚨 Error processing MQTT message: {e}")

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Retry MQTT connection
while True:
    try:
        print(f"🔄 Connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except Exception as e:
        print(f"🚨 MQTT Connection Failed: {e}, retrying in 5 seconds...")
        time.sleep(5)

def start_mqtt():
    mqtt_client.loop_start()
