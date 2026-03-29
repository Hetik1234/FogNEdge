import time
import random
import requests

FOG_NODE_URL = "http://localhost:5000/ingest"

def run_sensor():
    print("Starting HVAC Airflow Sensor...")
    while True:
        # HVAC running percentage
        airflow = random.randint(30, 100)
        
        payload = {"sensor_id": "HVAC_Main", "type": "hvac", "value": airflow}
        
        try:
            requests.post(FOG_NODE_URL, json=payload)
            print(f"[HVAC Sensor] Sent: {airflow}% capacity")
        except Exception:
            print("[HVAC Sensor] Fog Node offline. Waiting...")
            
        time.sleep(7) # Send every 7 seconds

if __name__ == "__main__":
    run_sensor()