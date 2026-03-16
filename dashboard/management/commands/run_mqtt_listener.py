from django.core.management.base import BaseCommand
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
from dashboard.models import VenueAlert

class Command(BaseCommand):
    help = 'Starts the AWS IoT MQTT Listener to receive Fog Node data'

    def custom_callback(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode('utf-8'))
            self.stdout.write(self.style.SUCCESS(f"Received Heartbeat: {payload['status']}"))
            
            VenueAlert.objects.create(
                status_priority=payload['status'],
                details=payload['details'],
                occupancy=payload.get('occupancy', 0),
                co2_level=payload.get('co2', 0),
                temperature=payload.get('temperature', 0.0),
                hvac_airflow=payload.get('hvac', 0)
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            
    def handle(self, *args, **options):
        self.stdout.write("Starting AWS IoT Listener for the Venue Dashboard...")

        # --- AWS Connection Setup ---
        # Note: The client ID must be different from the one used in your fog_node.py
        mqtt_client = AWSIoTMQTTClient("DjangoDashboardBackend")
        
        # TODO: Replace with your actual AWS IoT Custom Endpoint
        mqtt_client.configureEndpoint("a1xzyu0yv7w92y-ats.iot.us-east-1.amazonaws.com", 8883)
        
        # TODO: Ensure your certificates are copied into the main Django project folder
        mqtt_client.configureCredentials(
            "/home/ec2-user/environment/FogNEdge/certs/AmazonRootCA1.pem",
            "/home/ec2-user/environment/FogNEdge/certs/aaba5b4204d011bd48d62d5449ccb46df4f0d67a57b318b4d6e83c8722408508-private.pem.key",
            "/home/ec2-user/environment/FogNEdge/certs/aaba5b4204d011bd48d62d5449ccb46df4f0d67a57b318b4d6e83c8722408508-certificate.pem.crt"
            )
        try:
            self.stdout.write("Connecting to AWS IoT Core...")
            mqtt_client.connect()
            self.stdout.write(self.style.SUCCESS("Connected successfully! Listening for telemetry..."))

            # Subscribe to the exact same topic the Fog Node is publishing to
            mqtt_client.subscribe("venue/telemetry", 1, self.custom_callback)

            # Keep the listener running forever in the background
            while True:
                time.sleep(1)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to connect to AWS: {e}"))