import time
import random
import requests

FOG_NODE_URL = "http://localhost:5000/ingest"

def run_sensor():
    print("Starting CO2 Sensor...")
    while True:
        # Realistic CO2 levels (400 is fresh air, >1000 is stuffy)
        co2_level = random.randint(400, 1200)
        payload = {"sensor_id": "CO2_Zone_1", "type": "co2", "value": co2_level}
        
        try:
            requests.post(FOG_NODE_URL, json=payload)
            print(f"[CO2 Sensor] Sent: {co2_level} ppm")
        except Exception as e:
            print("[CO2 Sensor] Fog Node offline. Waiting...")
            
        time.sleep(4) # Send every 4 seconds

if __name__ == "__main__":
    run_sensor()