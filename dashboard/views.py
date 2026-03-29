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
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            recent_items = items[:25] 
            
            history_list = []
            for item in recent_items:
                raw_time = item.get('timestamp', '')
                formatted_time = raw_time[11:19] if len(raw_time) > 18 else raw_time
                
                # Force uppercase to make keyword matching bulletproof
                venue_status = item.get('venue_status', 'NORMAL').upper()
                
                # --- NEW 3-TIER COLOR LOGIC ---
                if "SEVERE" in venue_status or "CRITICAL" in venue_status:
                    badge_color = "danger" # RED
                    action_details = "CRITICAL: Air quality severely degraded. Maximum HVAC required."
                elif "CAUTION" in venue_status:
                    badge_color = "warning text-dark" # YELLOW (with dark text for readability)
                    action_details = "Threshold exceeded: High CO2 detected. Adjusting ventilation."
                else:
                    badge_color = "success" # GREEN
                    action_details = "All environmental metrics are within normal operating parameters."
                
                history_list.append({
                    'status': venue_status,
                    'details': action_details,
                    'color': badge_color, 
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
                        
    except Exception as e:
        print(f"DynamoDB Error: {e}")
        return JsonResponse({'history': []}, status=500)