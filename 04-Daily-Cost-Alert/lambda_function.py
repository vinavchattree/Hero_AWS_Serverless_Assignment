import logging
import datetime
import boto3
import json
import os
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_email(threshold):
    region = os.environ["REGION"]
    topic = os.environ["TOPIC"]
    sns_client = boto3.client("sns", region_name=region)
    try:
        response = sns_client.publish(
            TopicArn=topic,
            Subject=f"AWS cost above {threshold}",
            Message=f"Monthly data cost exceeded {threshold}"
        )
        logger.info("Mail sent")
        return 1
    except Exception as e:
        logger.info(f"Error while sending mail: {e}")
        return 0


def check_cost():
    logger.info("This method checks cost from start of month to current date")
    start_date = datetime.date.today().replace(day=1)
    today = datetime.date.today()

    if start_date == today:
        logger.info("Same start and end date. Exiting")
        return "skipped"

    logger.info(f"Getting result from cost explorer API with start date: {start_date} and end date: {today}")
    cost_explorer_client = boto3.client('ce', region_name='us-east-1')
    
    try:
        response = cost_explorer_client.get_cost_and_usage(
            TimePeriod={
                'Start': str(start_date),
                'End': str(today)
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        logger.info(f"Response from cost explorer API: {response}")

        cost = 0.0
        for item in response.get('ResultsByTime', []):
            cost = float(item.get('Total', {}).get('UnblendedCost', {}).get('Amount', 0.0))
        
        logger.info(f"cost: {cost}")
        
        threshold = float(os.environ['THRESHOLD'])
        if cost > threshold:
            if send_email(threshold) == 1:
                logger.info("Threshold exceeded and mail sent")
                return "success"
            else:
                logger.info("Threshold exceeded but failed to send mail")
                return "failed"
        else:
            logger.info(f"Cost is less than threshold. Cost: {cost} Threshold: {threshold}")
            return "ok"

    except ClientError as e:
        logger.error(f"Error while calling cost explorer API: {e}")
        return "error"


def lambda_handler(event, context):
    logger.info("Daily Cost Lambda started")

    status = check_cost()
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Cost Evaluation completed',
            'status': status
        })
    }