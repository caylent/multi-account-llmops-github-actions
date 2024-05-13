import argparse
import json
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def read_parameters(param_file):
    logging.info(f"Reading param_file from {param_file}")
    with open(param_file, "r") as f:
        params = json.load(f)

    parameters = params["Parameters"]
    tags = params["Tags"]

    paramlist = []
    for key in parameters:
        p = {
            "ParameterKey": key,
            "ParameterValue": parameters[key],
            "UsePreviousValue": False,
        }
        paramlist.append(p)

    taglist = []
    for key in tags.keys():
        t = {"Key": key, "Value": tags[key]}
        taglist.append(t)

    return paramlist, taglist

# assume cross account role
def assume_role(role_arn, session_name):
    sts_client = boto3.client("sts")
    try:
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=session_name
        )
        return assumed_role_object["Credentials"]
    except ClientError as e:
        logger.error(f"Error assuming role: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stack-name")
    parser.add_argument("--region")
    parser.add_argument("--param-file")
    parser.add_argument("--project-name")
    parser.add_argument("--role-arn")
    args, _ = parser.parse_known_args()

    # Configure logging to output the line number and message
    log_format = "%(levelname)s: [%(filename)s:%(lineno)s] %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)
    
    credentials = assume_role(args.role_arn, "cfn-deploy")

    cfn_client = boto3.client("cloudformation", region_name=args.region, 
                    aws_access_key_id=credentials["AccessKeyId"], 
                    aws_secret_access_key=credentials["SecretAccessKey"], 
                    aws_session_token=credentials["SessionToken"])
    stack_name = (
        args.project_name
        + "-"
        + args.stack_name
    )

    # Read parameters and tags
    parameters, tags = read_parameters(args.param_file)

    # Read Cfn template body
    with open("endpoint-config-template.yml", "r") as f:
        template_body = f.read()

    try:
        cfn_client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM'
            ],
            Tags=tags,
        )
        logging.info("Creating a new stack...")
    except cfn_client.exceptions.AlreadyExistsException:
        cfn_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM'
            ],
            Tags=tags,
        )
        logging.info("Updating existing stack...")
