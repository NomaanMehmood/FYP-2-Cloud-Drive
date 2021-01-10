import logging
import boto3
from botocore.exceptions import ClientError
s3 = boto3.client("s3",
                  endpoint_url='https://s3.wasabisys.com',
                  aws_access_key_id='E33PV586BD2CIMX6WPRE',
                  aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )


def upload_file(file_name, bucket):
    object_name = file_name
    s3_client = boto3.client('s3', endpoint_url='https://s3.wasabisys.com',
                             aws_access_key_id='E33PV586BD2CIMX6WPRE',
                             aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response


def download_file(file_name, bucket):
    s3 = boto3.resource('s3', endpoint_url='https://s3.wasabisys.com',
                        aws_access_key_id='E33PV586BD2CIMX6WPRE',
                        aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )
    output = f"C:/Users/noumy/OneDrive/Desktop/Cloud Drive FYP/downloads/{file_name}"

    s3.Bucket(bucket).download_file(file_name, output)
    return output

def list_files(bucket):
    s3 = boto3.client('s3', endpoint_url='https://s3.wasabisys.com',
                      aws_access_key_id='E33PV586BD2CIMX6WPRE',
                      aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)
    return contents



def create_presigned_url(bucket_name, object_name, expiration=3600):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', endpoint_url='https://s3.wasabisys.com',
                        aws_access_key_id='E33PV586BD2CIMX6WPRE',
                        aws_secret_access_key='FTew9pY7753z9upB7LneasdZl6ze9edEKMLRW7k0', )
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

