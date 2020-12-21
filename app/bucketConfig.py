import boto3
import uuid



import logging
import boto3
from botocore.exceptions import ClientError


def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True






s3_client = boto3.resource("s3" ,
                  endpoint_url='https://s3.wasabisys.com',
                  aws_access_key_id='E33PV586BD2CIMX6WPRE',
                  aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )


def deletefile(bucketname, filename):
    client = boto3.client('s3',
         endpoint_url = 'https://s3.wasabisys.com',
                        aws_access_key_id = 'E33PV586BD2CIMX6WPRE',
                                            aws_secret_access_key = 'FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0',
    )
    response = client.delete_object(Bucket=bucketname,Key=filename)
    return response


def showAllBucket():
    s3 = boto3.client('s3',
         endpoint_url = 'https://s3.wasabisys.com',
                        aws_access_key_id = 'E33PV586BD2CIMX6WPRE',
                                            aws_secret_access_key = 'FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0',
    )
    response = s3.list_buckets()

    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')
    return response


def create_bucket_name(bucket_prefix):
    # The generated bucket name must be between 3 and 63 chars long
    return ''.join([bucket_prefix, str(uuid.uuid4())])

def create_bucket(bucket_prefix, s3_connection):
    session = boto3.session.Session()
    current_region = session.region_name
    bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
        'LocationConstraint': current_region})

    return bucket_name
#print(create_bucket('zawali',s3_client))