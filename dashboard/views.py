from django.shortcuts import render
from django.http import JsonResponse
import boto3

# Initialize the DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 
table = dynamodb.Table('VenueTelemetry')

def dashboard_view(request):
    """Renders the main HTML dashboard page."""
    return render(request, 'dashboard/index.html')

def get_latest_alert(request):
    """API endpoint that grabs the newest alert directly from DynamoDB."""
    try:
        # Fetch all items from the table
        response = table.scan()
        items = response.get('Items', [])

        if items:
            # Sort the items by timestamp (newest first)
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            latest_alert = items[0]
            
            # Extract just the HH:MM:SS part from the ISO timestamp string
            raw_time = latest_alert.get('timestamp', '')
            formatted_time = raw_time[11:19] if len(raw_time) > 18 else raw_time

            data = {
                'status': latest_alert.get('status', 'SYSTEM_NORMAL'),
                'details': latest_alert.get('details', 'No details available.'),
                'time': formatted_time,
                'occupancy': int(latest_alert.get('occupancy', 0)),
                'co2': int(latest_alert.get('co2', 0)),
                'temperature': float(latest_alert.get('temperature', 0.0)),
                'hvac': int(latest_alert.get('hvac', 0))
            }
        else:
            # Fallback if the database is completely empty
            data = {
                'status': 'LOADING', 
                'details': 'Waiting for Lambda to write to DynamoDB...', 
                'time': '--:--:--', 
                'occupancy': 0, 'co2': 0, 'temperature': 0, 'hvac': 0
            }
            
        return JsonResponse(data)
        
    except Exception as e:
        print(f"DynamoDB Error: {e}")
        # Return a safe error state to the frontend instead of crashing
        return JsonResponse({
            'status': 'DATABASE_ERROR', 
            'details': 'Could not connect to DynamoDB.', 
            'time': '--:--:--',
            'occupancy': 0, 'co2': 0, 'temperature': 0, 'hvac': 0
        })