import paho.mqtt.client as mqtt
import redis
import json
from datetime import datetime

# Konfigurasi MQTT (Broker di VPS 1)
MQTT_HOST = "103.49.239.121"
MQTT_PORT = 1883
MQTT_USER = "myuser"
MQTT_PASS = "tugasakhir"
MQTT_TOPIC = "sensors/report"

# Konfigurasi Redis (Redis di VPS 2)
r = redis.Redis(
    host='103.217.145.62',      # VPS 2 IP
    port=6379,
    password='tugasakhir',      
    decode_responses=True
)

KEY_LOG = "sensor_data_log_r"
MAX_LOG = 100

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        data["timestamp"] = datetime.now().isoformat()

        # Simpan data ke Redis VPS 2
        r.set("latest_sensor_data_r", json.dumps(data))
        r.lpush(KEY_LOG, json.dumps(data))
        r.ltrim(KEY_LOG, 0, MAX_LOG - 1)

        print(f"[MQTT->Redis] Stored to VPS2: {data}")

    except Exception as e:
        print("[ERROR] Failed to handle message:", e)

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
