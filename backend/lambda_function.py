import json
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DBkhalidhashim.com')

def get_client_ip(event):
    # HTTP API IP format
    http_context = event.get('requestContext', {}).get('http', {})
    ip_address = http_context.get('sourceIp')

    # REST API IP format
    if not ip_address:
        ip_address = event.get('requestContext', {}).get('identity', {}).get('sourceIp')

    # Fallback: check headers
    if not ip_address:
        xff = event.get('headers', {}).get('X-Forwarded-For')
        if xff:
            ip_address = xff.split(',')[0].strip()

    return ip_address or 'unknown'

def lambda_handler(event, context):
    headers = event.get('headers', {})
    ip_address = get_client_ip(event)
    user_agent = headers.get('User-Agent', 'Unknown')

    visit_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    table.put_item(
        Item={
            'id': visit_id,
            'timestamp': timestamp,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
    )

    print(f"Logged visit: {visit_id} from IP {ip_address} using {user_agent}")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Visit logged', 'visit_id': visit_id})
    }


