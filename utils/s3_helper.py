import logging
import boto3
from botocore.exceptions import ClientError
import os
import pandas as pd
import io
import json

def upload_data_to_s3(data, bucket, key):
    """Upload a file to an S3 bucket

    :param data: data to upload
    :param bucket: Bucket to upload to
    :param key: S3 object key
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        object_key = r'{0}/{1}'.format(key, "results_summary.json")
        s3_uri = r's3://{0}/{1}'.format(bucket, object_key)
        response = s3_client.put_object(
                 Body=json.dumps(data, indent=4),
                 Bucket=bucket,
                 Key=object_key
                )
    except ClientError as e:
        logging.error(e)
        return False
    print("Data upload successfull s3_uri: ", s3_uri)
    return True


def upload_dataframe_to_s3(bucket_name, object_name, file_name, df):
    """Upload a dataframe to an S3 bucket

    :param bucket: Bucket to upload to
    :param object_name: S3 object name
    :param df: dataframe to upload
    :return: True if file was uploaded, else False
    """
    s3_uri = r's3://{0}/{1}/{2}'.format(bucket_name, object_name, file_name)
    df.to_csv(s3_uri, index=False)


def read_s3_csv_to_dataframe(bucket, s3_file_key):
    """
    Read a CSV file from an S3 bucket into a Pandas DataFrame.

    Parameters:
        bucket (str): The name of the S3 bucket.
        s3_file_key (str): The key (path) of the CSV file in the S3 bucket.

    Returns:
        pandas.DataFrame: The DataFrame containing the CSV data.
    """
    # Initialize S3 client
    s3 = boto3.client('s3')
    
    # Read CSV file from S3
    obj = s3.get_object(Bucket=bucket, Key=s3_file_key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))
    
    return df