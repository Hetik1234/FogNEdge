import time
import random
import requests

FOG_NODE_URL = "http://localhost:5000/ingest"

def run_sensor():
    print("Starting Temperature Sensor...")
    temp = 20.0
    while True:
        # Fluctuate temperature slightly
        temp += random.uniform(-0.5, 0.5)
        temp = round(temp, 2)
        
        payload = {"sensor_id": "Temp_Lane_4", "type": "temperature", "value": temp}
        
        try:
            requests.post(FOG_NODE_URL, json=payload)
            print(f"[Temp Sensor] Sent: {temp} °C")
        except Exception:
            print("[Temp Sensor] Fog Node offline. Waiting...")
            
        time.sleep(6) # Send every 6 seconds

if __name__ == "__main__":
    run_sensor()