import json
import boto3
import logging
import os
from botocore.exceptions import ClientError
from collections import defaultdict

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client=boto3.client('s3')
PUBLIC_GROUPS = [
    "http://acs.amazonaws.com/groups/global/AllUsers",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
]

def is_public_access_block(bucket_name):
    print("get_public_access_block")
    print(bucket_name)
    response=s3_client.get_public_access_block(Bucket=bucket_name)
    logger.info(f"public access {response}")
    for key,value in response["PublicAccessBlockConfiguration"].items():
        logger.info(f"bucket {bucket_name}, {key},{value}")
        if value is False:
            return False
    return True

def is_public_policy(bucket_name):    
    logger.info("get_policy")
    try:
        response=s3_client.get_bucket_policy_status(Bucket=bucket_name)
        logger.info(f"policy access {response}")
        if response['PolicyStatus']['IsPublic'] is False:
            return False
        
        return True
    except ClientError as e:
        if "The bucket policy does not exist" in str(e) :
            return False

def is_ACL_Access(bucket_name):
    try:
     print(f"is_ACL_Access for {bucket_name}")          
     response=s3_client.get_bucket_acl(Bucket=bucket_name)
     logger.info(f"response acl= {response}")
    
     for grant in response.get("Grants", []):
            grantee = grant.get("Grantee", {})
            if grantee.get("Type") == "Group" and grantee.get("URI") in PUBLIC_GROUPS:
                return True
     return False
    except Exception as e:
        print(e)
        if "AccessControlListNotSupported" in str(e) :
            return False


def postEmail(topicName,subject,body):    
    sns_client=boto3.client('sns')
    try:
        logger.info('Sending email with public bucket ')
        response=sns_client.publish(TopicArn=topicName, 
                                Subject=subject,
                                Message=body
                                )
        logger.info('Email sent')
    except ClientError as e:
        print({e})

def lambda_handler(event, context):
    # TODO implement
        logger.info("getting all buckets from s3")
        response=s3_client.list_buckets()
        logger.info(response)
    
        bucket_access=defaultdict(list)
        logger.info('Checking access for all buckets')
        for bucket in response['Buckets'] :
            bucket_name=bucket["Name"]
            try:
                if not is_public_access_block(bucket_name):
                    bucket_access[bucket_name].append('public access not blocked')
                if is_public_policy(bucket_name):
                    bucket_access[bucket_name].append('policy status is public')
                if is_ACL_Access(bucket_name):
                    bucket_access[bucket_name].append('Public access allowed in access control list')


            except ClientError as e :
                print(e)
        message=""   
        topic=os.environ['topic']
        for key, value in bucket_access.items():
            reasons=",".join(value)
            message+=f"\n Bucket name:{key} is public due to following reasons: {reasons}"
            logger.info(f"key:{key} value:{value}")    
        if  bucket_access:            
            postEmail(topic,'S3 public bucket alert',message)      

        return {
        'statusCode': 200,
        'body': json.dumps('Successfully checked for public buckets')
        }
