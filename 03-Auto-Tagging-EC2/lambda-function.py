import os
import time  # Fixed: Added missing import
import boto3
from datetime import datetime, timezone

ec2 = boto3.client('ec2')
cloudtrail = boto3.client('cloudtrail')

def get_instance_owner_with_retry(instance_id, max_retries=6, delay_seconds=10):
    
    for attempt in range(max_retries):
        try:
            response = cloudtrail.lookup_events(
                LookupAttributes=[
                    {'AttributeKey': 'ResourceName', 'AttributeValue': instance_id},
                    {'AttributeKey': 'EventName', 'AttributeValue': 'RunInstances'}
                ],
                MaxResults=1
            )
            events = response.get('Events', [])
            if events and events[0].get('Username'):
                return events[0].get('Username')
        except Exception as e:
            print(f"CloudTrail lookup failed on attempt {attempt+1}: {str(e)}")
            
        
        time.sleep(delay_seconds)
        
    return "UnknownOwner"

def lambda_handler(event, context):
    instance_id = event['detail']['instance-id']
    launch_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    environment = os.getenv('ENVIRONMENT', 'Production')
    
   
    owner = get_instance_owner_with_retry(instance_id)
    
    
    tags = [
        {'Key': 'LaunchDate', 'Value': launch_date},
        {'Key': 'Environment', 'Value': environment},
        {'Key': 'Owner', 'Value': owner},
        {'Key': 'AutoTagged', 'Value': 'True'}
    ]
    
    
    ec2.create_tags(
        Resources=[instance_id],
        Tags=tags
    )
    
    message = f"Successfully tagged instance {instance_id} | LaunchDate: {launch_date}, Environment: {environment}, Owner: {owner}"
    print(message)
    
    return {
        'statusCode': 200,
        'body': message
    }