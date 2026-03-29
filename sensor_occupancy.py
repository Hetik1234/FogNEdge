import time
import random
import requests

FOG_NODE_URL = "http://localhost:5000/ingest"

def run_sensor():
    print("Starting Occupancy Sensor...")
    # Base occupancy
    occupancy = 160 
    while True:
        # Simulate people walking in and out of the bowling venue
        occupancy += random.randint(-5, 8)
        occupancy = max(0, min(occupancy, 300)) # Keep between 0 and 300
        
        payload = {"sensor_id": "Occ_Entrance", "type": "occupancy", "value": occupancy}
        
        try:
            requests.post(FOG_NODE_URL, json=payload)
            print(f"[Occupancy Sensor] Sent: {occupancy} people")
        except Exception:
            print("[Occupancy Sensor] Fog Node offline. Waiting...")
            
        time.sleep(5) # Send every 5 seconds

if __name__ == "__main__":
    run_sensor()