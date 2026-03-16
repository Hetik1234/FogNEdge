from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import random
import threading
import json
from queue import Queue
from datetime import datetime

# ---------------------------------------------------------
# 1. SENSOR LAYER
# ---------------------------------------------------------
class MockSensor(threading.Thread):
    def __init__(self, sensor_id, sensor_type, frequency_seconds, data_queue):
        super().__init__()
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.frequency_seconds = frequency_seconds
        self.data_queue = data_queue
        self.daemon = True 

    def generate_value(self):
        if self.sensor_type == 'occupancy': return int(random.uniform(5, 45))
        elif self.sensor_type == 'co2_level': return int(random.uniform(400, 1200))
        elif self.sensor_type == 'temperature': return round(random.uniform(20.0, 27.0), 1)
        elif self.sensor_type == 'hvac_airflow': return int(random.uniform(10, 95))
        return 0

    def run(self):
        while True:
            payload = {"sensor_id": self.sensor_id, "type": self.sensor_type, "value": self.generate_value()}
            self.data_queue.put(payload)
            time.sleep(self.frequency_seconds)

# ---------------------------------------------------------
# 2. VIRTUAL FOG NODE LAYER (AWS IoT Integrated)
# ---------------------------------------------------------
class VirtualFogNode:
    def __init__(self, data_queue):
        self.data_queue = data_queue
        self.current_state = {'occupancy': 0, 'co2_level': 400, 'temperature': 22.0, 'hvac_airflow': 0}
        self.hvac_struggling_counter = 0

        # --- AWS IoT Core Setup ---
        self.mqtt_client = AWSIoTMQTTClient("VenueFogNode")
        
        # TODO: Replace with your actual AWS IoT Custom Endpoint
        self.mqtt_client.configureEndpoint("a1xzyu0yv7w92y-ats.iot.us-east-1.amazonaws.com", 8883)
        
        # TODO: Ensure these match the exact filenames you uploaded to Cloud9
        self.mqtt_client.configureCredentials(
            "/home/ec2-user/environment/FogNEdge/certs/AmazonRootCA1.pem",
            "/home/ec2-user/environment/FogNEdge/certs/aaba5b4204d011bd48d62d5449ccb46df4f0d67a57b318b4d6e83c8722408508-private.pem.key",
            "/home/ec2-user/environment/FogNEdge/certs/aaba5b4204d011bd48d62d5449ccb46df4f0d67a57b318b4d6e83c8722408508-certificate.pem.crt"
        )

        print("Connecting to AWS IoT Core...")
        self.mqtt_client.connect()
        print("Connected successfully!\n")

    def process_incoming_data(self):
        # Starts the decision engine in the background
        threading.Thread(target=self.evaluate_interdependent_state, daemon=True).start()
        
        while True:
            if not self.data_queue.empty():
                raw_data = self.data_queue.get()
                self.current_state[raw_data['type']] = raw_data['value']
            time.sleep(0.1)

    def evaluate_interdependent_state(self):
        while True:
            occ = self.current_state['occupancy']
            co2 = self.current_state['co2_level']
            temp = self.current_state['temperature']
            airflow = self.current_state['hvac_airflow']

            # Default state
            status = "SYSTEM_NORMAL"
            details = "All sensors nominal. Venue environment optimal."

            # Evaluate interdependent thresholds
            if occ > 20 and co2 > 1000 and temp < 24.0:
                status = "ROUTINE_ACTION"
                details = "Opened fresh air vents (High CO2, Normal Temp)."
            elif occ > 20 and co2 > 1000 and temp >= 24.0:
                status = "HVAC_ACTION"
                details = "Engaged AC Compressor (High CO2, High Temp)."
            
            if temp >= 25.0 and airflow > 80:
                self.hvac_struggling_counter += 1
                if self.hvac_struggling_counter >= 3:
                    status = "CRITICAL_MAINTENANCE"
                    details = "AC at max capacity but temperature remains high!"
            else:
                self.hvac_struggling_counter = 0

            # Package the entire state and dispatch it
            payload = {
                "status": status,
                "details": details,
                "occupancy": occ,
                "co2": co2,
                "temperature": temp,
                "hvac": airflow,
                "timestamp": datetime.utcnow().isoformat()
            }
            json_payload = json.dumps(payload)
            
            # Publish to AWS
            self.mqtt_client.publish("venue/telemetry", json_payload, 1)
            print(f"[*] PUBLISHED: {status} | Temp: {temp}°C | CO2: {co2}ppm | Occ: {occ}")
            
            time.sleep(5) # Send heartbeat every 5 seconds

# ---------------------------------------------------------
# 3. MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    local_network_queue = Queue()

    sensors = [
        MockSensor("cam_zone_1", "occupancy", 2.0, local_network_queue),
        MockSensor("air_qual_1", "co2_level", 3.0, local_network_queue),
        MockSensor("therm_1", "temperature", 4.0, local_network_queue),
        MockSensor("vent_monitor_1", "hvac_airflow", 2.0, local_network_queue)
    ]

    for sensor in sensors: sensor.start()

    fog_node = VirtualFogNode(local_network_queue)
    try:
        fog_node.process_incoming_data()
    except KeyboardInterrupt:
        print("\nSimulation stopped.")