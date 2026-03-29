from django.shortcuts import render
from django.http import JsonResponse
import boto3
from decimal import Decimal

# Using the Ireland region from your configuration
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1') 
table = dynamodb.Table('VenueTelemetry')

def dashboard_view(request):
    return render(request, 'dashboard/index.html')

def get_latest_alert(request):
    try:
        response = table.scan()
        items = response.get('Items', [])

        if items:
            # Sort newest to oldest and grab the top 25
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            recent_items = items[:25] 
            
            history_list = []
            for item in recent_items:
                raw_time = item.get('timestamp', '')
                formatted_time = raw_time[11:19] if len(raw_time) > 18 else raw_time
                
                history_list.append({
                    # Mapped exactly to the Lambda DynamoDB payload
                    'status': item.get('venue_status', 'SYSTEM_NORMAL'),
                    'time': formatted_time,
                    'occupancy': int(item.get('occupancy', 0)),
                    'co2': int(item.get('co2', 0)),
                    'temperature': float(item.get('temperature', 0.0)),
                    'hvac': int(item.get('hvac', 0))
                })
                
            return JsonResponse({'history': history_list})
        else:
            return JsonResponse({'history': []})
            
    except Exception as e:
        print(f"DynamoDB Error: {e}")
        return JsonResponse({'history': []}, status=500)