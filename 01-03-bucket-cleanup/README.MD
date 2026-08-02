1) For s3 cleanup I added some objects to s3 using following python prog with boto 3 :

import boto3

def add_new_object():
    print(&#39;hello&#39;)
    BUCKET_NAME=&#39;learn-cli-vinav&#39;
    s3_client=boto3.client(&#39;s3&#39;)
    try:
        for i in range (2000):
            filename=f&quot;vin{i}.txt&quot;
            print(f&quot;filename {filename}&quot;)
            response=s3_client.put_object(
                    Body=b&quot;hello&quot;,
                    Bucket=BUCKET_NAME,
                    Key=filename
                    )
            if (i + 1) % 500 == 0:
                print(f&quot;Uploaded {i + 1}/2000 files...&quot;)
               
        print(&quot;Upload complete!&quot;)
    except Exception as e:
        print(f&quot;Error {e}&quot;)

add_new_object()

2) Basically what I did was tried to get all the objects in the bucket using paginator  page size 100
    I then checked each object date recieved in lastmodified with current date and called DeleteObject  to delete it 

3) But I was getting timeout error as I was trying to delete too may objects seperately

4) To handle this I switched to bulk deletion method in boto3
