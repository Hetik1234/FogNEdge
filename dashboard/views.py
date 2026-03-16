import json
import boto3
import uuid

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VenueTelemetry')

def lambda_handler(event, context):
    # SQS sends messages in 'Records' batches
    for record in event['Records']:
        # The actual IoT JSON payload is stored inside the SQS body
        payload = json.loads(record['body'])
        
        # DynamoDB requires floats to be converted to strings to avoid precision errors
        temp_string = str(payload['temperature'])
        
        # Write the data to DynamoDB
        table.put_item(
            Item={
                'alert_id': str(uuid.uuid4()), # Generates a unique ID for the database
                'timestamp': payload['timestamp'],
                'status': payload['status'],
                'details': payload['details'],
                'occupancy': payload['occupancy'],
                'co2': payload['co2'],
                'temperature': temp_string, 
                'hvac': payload['hvac']
            }
        )
        print(f"Successfully saved to DynamoDB: {payload['status']}")
        
    return {"statusCode": 200, "body": "Successfully processed SQS queue."}