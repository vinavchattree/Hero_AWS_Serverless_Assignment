import json
import logging
import os
from datetime import datetime, timezone
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
def lambda_handler(event, context):
   s3_client=boto3.client('s3')
   delete_list: list[str]=[]
   

   try:
        paginator=s3_client.get_paginator('list_objects_v2')
        bucket=os.environ["BUCKET"]
        threshold=int(os.environ["CUTOFF"])
        page_iterator=paginator.paginate(
            Bucket=bucket,
            PaginationConfig={'PageSize':100}
            )
        current_date=datetime.now().replace(tzinfo=timezone.utc)
        logger.info(f"current_date{current_date}")
        objects_to_delete = []
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:                    

                    key=obj["Key"]                   
                   
                    last_modified=obj['LastModified']
                    
                    logger.info(f"Key {obj['Key']}")
                    logger.info(f"LastChangeDate:{last_modified}")                   
                    
                    time_differnce=current_date-last_modified               
                    logger.info(f"timediff in days {time_differnce.days}")
                    if(time_differnce.days>=threshold):
                        logger.info(f"{obj['Key']} will be deleted")
                        objects_to_delete.append({'Key': obj["Key"]})
                        delete_list.append(obj['Key'])
                        if len(objects_to_delete)>=100:
                          s3_client.delete_objects(
                                                 Bucket=bucket,
                                                 Delete={'Objects':objects_to_delete}
                                             )
                          objects_to_delete = []
        if objects_to_delete:
            s3_client.delete_objects(
                Bucket=bucket,
                Delete={'Objects':objects_to_delete}
            )

   except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
   return {
        'statusCode': 200,
        'body': json.dumps({"deleted_files list": delete_list})
    }
