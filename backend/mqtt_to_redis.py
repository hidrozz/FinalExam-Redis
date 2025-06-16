import paho.mqtt.client as mqtt
import redis
import json
from datetime import datetime

# Konfigurasi MQTT
MQTT_HOST = "103.23.198.211"
MQTT_PORT = 1883
MQTT_USER = "myuser"
MQTT_PASS = "tugasakhir"
MQTT_TOPIC = "sensors/report"

# Konfigurasi Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
KEY_LOG = "sensor_data_log"
MAX_LOG = 100

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        data["timestamp"] = datetime.now().isoformat()

        r.set("latest_sensor_data", json.dumps(data))
        r.lpush(KEY_LOG, json.dumps(data))
        r.ltrim(KEY_LOG, 0, MAX_LOG - 1)

        print(f"[MQTT->Redis] Stored: {data}")

    except Exception as e:
        print("[ERROR] Failed to handle message:", e)

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
