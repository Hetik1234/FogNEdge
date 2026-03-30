from flask import Flask, request, jsonify
import threading
import time
import datetime
import json
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# ==========================================
# AWS IOT CORE CONFIGURATION - UPDATE THESE!
# ==========================================
ENDPOINT = "a2jhzm8175r7at-ats.iot.eu-west-1.amazonaws.com"
CLIENT_ID = "SmartVenueFogNode"
PATH_TO_CERT = r"C:\Users\hetik\Downloads\Fog&EdgeComputing\Project\FogNEdge\certs\7c525fdea28690d6266252c21292f268d2bc510967e34603b7127cd702661334-certificate.pem.crt"
PATH_TO_KEY = r"C:\Users\hetik\Downloads\Fog&EdgeComputing\Project\FogNEdge\certs\7c525fdea28690d6266252c21292f268d2bc510967e34603b7127cd702661334-private.pem.key"
PATH_TO_ROOT = r"C:\Users\hetik\Downloads\Fog&EdgeComputing\Project\FogNEdge\certs\AmazonRootCA1.pem"
TOPIC = "venue/telemetry"
# ==========================================

app = Flask(__name__)

venue_state = {
    "co2": 0,
    "occupancy": 0,
    "temperature": 0.0,
    "hvac": 0
}

# Initialize AWS MQTT Connection
print("Connecting to AWS IoT Core...")
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=PATH_TO_CERT,
    pri_key_filepath=PATH_TO_KEY,
    ca_filepath=PATH_TO_ROOT,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=30
)
connect_future = mqtt_connection.connect()
connect_future.result()
print("Connected securely to AWS IoT Core!")

@app.route('/ingest', methods=['POST'])
def ingest_data():
    data = request.json
    sensor_type = data.get("type")
    value = data.get("value")
    if sensor_type in venue_state:
        venue_state[sensor_type] = value
    return jsonify({"status": "received"}), 200

def process_and_publish():
    while True:
        time.sleep(10) 
        
        status = "NORMAL"
        if venue_state["co2"] > 1000 and venue_state["occupancy"] > 150:
            status = "CAUTION: VENTILATION REQUIRED"

        else if  venue_state["co2"] > 1100 and venue_state["occupancy"] > 200:
            status = "CRITICAL: VENTILATION REQUIRED ASAP"   
        payload = {
            "timestamp": datetime.datetime.now().isoformat(),
            "venue_status": status,
            "telemetry": venue_state.copy()
        }
        
        print(f"\n[FOG NODE] Aggregated Data: {payload}")
        
        # Publish to AWS IoT Core
        mqtt_connection.publish(
            topic=TOPIC,
            payload=json.dumps(payload),
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"[AWS] Successfully published to topic: {TOPIC}")

if __name__ == "__main__":
    threading.Thread(target=process_and_publish, daemon=True).start()
    app.run(port=5000, debug=False)