"""
This script is used to replicate the model artifacts cross-region and cross-account.

Below is the list of steps that are executed in the script:
- read the S3 Model Data URL from the parameters file
- replicate the model artifacts to the target region
"""

import boto3
import argparse
import json
import botocore
import logging

logger = logging.getLogger(__name__)

def assume_role(role_arn, session_name, region):
    sts_client = boto3.client('sts', region_name=region)
    try:
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        return assumed_role_object['Credentials']
    except botocore.exceptions.ClientError as e:
        print(f"Error assuming role: {e}")
        return None

def upload_file_to_s3(file_path, bucket, key, credentials, region):
    s3_client = boto3.client(
        's3',
        region_name=region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    try:
        s3_client.upload_file(file_path, bucket, key)
        print(f"Uploaded {file_path} to s3://{bucket}/{key}")
    except botocore.exceptions.ClientError as e:
        print(f"Failed to upload {file_path} to s3://{bucket}/{key}: {e}")

def copy_s3_objects(src_bucket_name, src_prefix, dest_bucket_name, dest_prefix, credentials, dest_region):
    # Create a new S3 client using the assumed role credentials
    s3_client = boto3.client(
        's3',
        region_name=dest_region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    # List all objects in the source bucket and prefix
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=src_bucket_name, Prefix=src_prefix):
        for obj in page.get('Contents', []):
            src_key = obj['Key']
            dest_key = dest_prefix + src_key[len(src_prefix):]  # Maintain the suffix of the source key in the destination key
            try:
                # Copy each object individually
                s3_client.copy(
                    {'Bucket': src_bucket_name, 'Key': src_key},
                    dest_bucket_name,
                    dest_key
                )
                print(f"Copied {src_key} to {dest_key}")
            except botocore.exceptions.ClientError as e:
                print(f"Error copying {src_key} to {dest_key}: {e}")

def get_model_data_url_from_config(config_file_path):
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    return config['Parameters']['ModelDataUrl']

def update_config_file(config_file_path, dest_bucket_name, dest_prefix, lambda_s3_key, stack_name):
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    config['Parameters']['ModelDataUrl'] = f"s3://{dest_bucket_name}/{dest_prefix}"
    config['Parameters']['ApiFunctionSourceCodeBucket'] = dest_bucket_name
    config['Parameters']['ApiFunctionSourceCodeKey'] = lambda_s3_key
    
    # Dynamically update the handler based on the use case
    handler_name = "inference_lambda_email_type.lambda_handler" if stack_name == "email-type" else "inference_lambda_email_names.lambda_handler"
    config['Parameters']['ApiFunctionHandler'] = handler_name
    
    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4)

def main(args):
    # Read the Model Data URL from the parameters file
    model_data_url = get_model_data_url_from_config(args.param_file)
    src_bucket_name = model_data_url.split('/')[2]
    src_prefix = '/'.join(model_data_url.split('/')[3:])
    # logger.info(f"Model Data URL: {model_data_url}")
    # logger.info(f"Source Bucket: {src_bucket_name}")
    # logger.info(f"Source Prefix: {src_prefix}")
    print(f"Model Data URL: {model_data_url}")
    print(f"Source Bucket: {src_bucket_name}")
    print(f"Source Prefix: {src_prefix}")

    # Assume the role in the destination account
    credentials = assume_role(args.role_arn, "s3-replicate", args.region_deploy)

    print(f"Dest Bucket: {args.dest_bucket}")
    print(f"Dest regions: {args.region_deploy}")
    
    # Upload Lambda zip to S3
    upload_file_to_s3(args.lambda_zip_path, args.dest_bucket, args.lambda_s3_key, credentials, args.region_deploy)
    
    # Copy the model artifacts to the destination bucket
    copy_s3_objects(src_bucket_name, src_prefix, args.dest_bucket, src_prefix, credentials, args.region_deploy)
    
    # update the config file with the destination bucket name
    update_config_file(args.param_file, args.dest_bucket, src_prefix, args.lambda_s3_key, args.stack_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", required=True, help="Source AWS Region of the S3 bucket")
    parser.add_argument("--region-deploy", required=True, help="Destination AWS Region for deployment")
    parser.add_argument("--role-arn", required=True, help="ARN of the role to assume for deployment in the destination account")
    parser.add_argument("--param-file", required=True, help="Path to the staging-config-export.json file")
    parser.add_argument("--dest-bucket", required=True, help="Destination S3 bucket name")
    parser.add_argument("--lambda-zip-path", required=True, help="Path to the Lambda zip file")
    parser.add_argument("--lambda-s3-key", required=True, help="S3 key for the Lambda zip file")
    parser.add_argument("--stack-name", required=True, help="Name of the stack")
    
    args = parser.parse_args()
    main(args)
