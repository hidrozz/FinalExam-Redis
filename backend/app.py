from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import redis
import json
import time
from datetime import datetime
import threading
import paho.mqtt.publish as publish

app = Flask(__name__)
CORS(app)

# Redis setup
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
KEY_LOG = "sensor_data_log"
RELAY_LOG = "relay_log"
MAX_LOG = 100
MAX_LOG_RELAY = 100

THRESHOLD_SOIL = 50  # dalam persentase kelembapan
ADC_DRY = 3000       # ADC saat kering
ADC_WET = 1000       # ADC saat basah

# MQTT relay command publisher
def publish_relay_status(status):
    publish.single(
        "sensors/moist_threshold",
        payload=status,
        hostname="103.23.198.211",
        port=1883,
        auth={'username': 'myuser', 'password': 'tugasakhir'}
    )

# Helper: log event relay
def log_relay_event(status, source):
    event = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "source": source
    }
    r.lpush(RELAY_LOG, json.dumps(event))
    r.ltrim(RELAY_LOG, 0, MAX_LOG_RELAY - 1)

# API: ambil status sensor & relay
@app.route("/api/status")
def get_status():
    latest = r.get("latest_sensor_data")
    relay_status = r.get("relay_status") or "OFF"
    mode = r.get("mode") or "AUTO"

    if latest:
        data = json.loads(latest)
        soil_adc = data.get("soil_moist")

        if soil_adc is not None:
            try:
                soil_adc = float(soil_adc)
                moisture_percent = max(0, min(100, 100 - ((soil_adc - ADC_WET) / (ADC_DRY - ADC_WET) * 100)))
                data["soil_percent"] = round(moisture_percent, 1)

                if moisture_percent < 35:
                    data["soil_label"] = "Kering"
                elif 35 <= moisture_percent <= 70:
                    data["soil_label"] = "Normal"
                else:
                    data["soil_label"] = "Basah"
            except:
                data["soil_percent"] = None
                data["soil_label"] = None
        else:
            data["soil_percent"] = None
            data["soil_label"] = None

        try:
            ph = float(data.get("soil_temp", 0))
            if 0 <= ph <= 14:
                if ph < 5.5:
                    data["ph_label"] = "Asam"
                elif ph <= 7.5:
                    data["ph_label"] = "Netral"
                else:
                    data["ph_label"] = "Basa"
            else:
                data["ph_label"] = "Invalid"
        except:
            data["ph_label"] = "Invalid"
    else:
        data = {
            "soil_moist": None,
            "soil_temp": "--",
            "env_hum": "--",
            "env_temp": "--",
            "soil_percent": None,
            "soil_label": None,
            "ph_label": None
        }

    data["relay_status"] = relay_status
    data["mode"] = mode
    return jsonify(data)

# API: toggle relay manual
@app.route("/api/relay-toggle", methods=["POST"])
def toggle_relay():
    current = r.get("relay_status") or "OFF"
    new_status = "OFF" if current == "ON" else "ON"
    r.set("relay_status", new_status)
    log_relay_event(new_status, "manual")
    publish_relay_status(new_status)
    return jsonify({"relay_status": new_status})

# API: toggle mode manual/auto
@app.route("/api/auto-mode-toggle", methods=["POST"])
def toggle_auto_mode():
    current = r.get("mode") or "AUTO"
    new_mode = "MANUAL" if current == "AUTO" else "AUTO"
    r.set("mode", new_mode)
    return jsonify({"mode": new_mode})

# API: data chart
@app.route("/api/chart-data")
def chart_data():
    raw_data = r.lrange(KEY_LOG, 0, 60)
    data = [json.loads(d) for d in raw_data if "timestamp" in json.loads(d)]

    labels = [datetime.fromisoformat(d["timestamp"]).strftime("%H:%M:%S") for d in data]
    soil = [d.get("soil_moist", 0) for d in data]
    temp = [d.get("env_temp", 0) for d in data]
    hum = [d.get("env_hum", 0) for d in data]
    ph = [d.get("soil_temp", 0) for d in data]

    return jsonify({
        "labels": labels[::-1],
        "soil": soil[::-1],
        "temperature": temp[::-1],
        "humidity": hum[::-1],
        "ph": ph[::-1]
    })

# API: log relay
@app.route("/api/relay-log")
def get_relay_log():
    raw_logs = r.lrange(RELAY_LOG, 0, MAX_LOG_RELAY)
    logs = [json.loads(item) for item in raw_logs]
    return jsonify(logs)

# Frontend files
@app.route("/")
def serve_dashboard():
    return send_from_directory('../frontend', 'index.html')

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory('../frontend/css', filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory('../frontend/js', filename)

# AUTO relay controller
def auto_control_logic():
    latest = r.get("latest_sensor_data")
    mode = r.get("mode") or "AUTO"

    if not latest or mode != "AUTO":
        return

    try:
        data = json.loads(latest)
        soil_adc = float(data.get("soil_moist", 0))
        moisture_percent = max(0, min(100, 100 - ((soil_adc - ADC_WET) / (ADC_DRY - ADC_WET) * 100)))
        current_status = r.get("relay_status") or "OFF"

        if moisture_percent < THRESHOLD_SOIL and current_status != "ON":
            r.set("relay_status", "ON")
            log_relay_event("ON", "auto")
            publish_relay_status("ON")
            print(f"[AUTO] Relay ON (Moisture: {moisture_percent:.1f}%)")

        elif moisture_percent >= THRESHOLD_SOIL and current_status != "OFF":
            r.set("relay_status", "OFF")
            log_relay_event("OFF", "auto")
            publish_relay_status("OFF")
            print(f"[AUTO] Relay OFF (Moisture: {moisture_percent:.1f}%)")

    except Exception as e:
        print("[AUTO ERROR]", e)

def auto_loop():
    while True:
        auto_control_logic()
        time.sleep(5)

threading.Thread(target=auto_loop, daemon=True).start()

# Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
