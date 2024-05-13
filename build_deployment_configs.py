import argparse
import json
import logging
import os
import sagemaker

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_approved_package(model_package_group_name, sm_client):
    """Gets the latest approved model package for a model package group.

    Args:
        model_package_group_name: The model package group name.

    Returns:
        The SageMaker Model Package ARN.
    """
    try:
        # Get the latest approved model package
        response = sm_client.list_model_packages(
            ModelPackageGroupName=model_package_group_name,
            ModelApprovalStatus="Approved",
            SortBy="CreationTime",
            MaxResults=100,
        )
        approved_packages = response["ModelPackageSummaryList"]

        # Fetch more packages if none returned with continuation token
        while len(approved_packages) == 0 and "NextToken" in response:
            logger.debug(
                "Getting more packages for token: {}".format(
                    response["NextToken"]
                )
            )
            response = sm_client.list_model_packages(
                ModelPackageGroupName=model_package_group_name,
                ModelApprovalStatus="Approved",
                SortBy="CreationTime",
                MaxResults=100,
                NextToken=response["NextToken"],
            )
            approved_packages.extend(response["ModelPackageSummaryList"])

        # Return error if no packages found
        if len(approved_packages) == 0:
            error_message = f"No approved ModelPackage found."
            logger.error(error_message)
            raise Exception(error_message)

        # Return the pmodel package arn
        model_package_arn = approved_packages[0]["ModelPackageArn"]
        logger.debug(
            f"Identified the latest approved model package: {model_package_arn}"
        )
        return model_package_arn
    except ClientError as e:
        error_message = e.response["Error"]["Message"]
        logger.error(error_message)
        raise Exception(error_message)

def extend_config(
    args,
    sagemaker_image_uri,
    model_config,
    stage_config,
    sm_client,
    project_id,
    project_arn,
    model_execution_role,
):
    """
    Extend the stage configuration with additional parameters and tags based.
    """
    # Verify that config has parameters and tags sections
    if (
        not "Parameters" in stage_config
        or not "StageName" in stage_config["Parameters"]
    ):
        raise Exception("Configuration file must include SageName parameter")
    if not "Tags" in stage_config:
        stage_config["Tags"] = {}
    # Create new params and tags
    new_params = {
        "DeploymentVersion": model_config["DeploymentVersion"],
        "SageMakerProjectName": args.sagemaker_project_name,
        "SageMakerImageUri": sagemaker_image_uri,
        "ModelDataUrl": model_config["model_data_url"],
        "EndpointInstanceType": model_config["instance_type"],
        "EndpointScalingTargetValue": model_config.get("EndpointScalingTargetValue", "90"),
        "EndpointScalingMinCapacity": model_config.get("EndpointScalingMinCapacity", "1"),
        "EndpointScalingMaxCapacity": model_config.get("EndpointScalingMaxCapacity", "3"),
        "EndpointScaleInCooldown": model_config.get("EndpointScaleInCooldown", "300"),
        "EndpointScaleOutCooldown": model_config.get("EndpointScaleOutCooldown", "300"),
        "ModelExecutionRoleArn": model_execution_role,
        "StackName": args.stack_name,
    }
    new_tags = {
        "sagemaker:deployment-stage": stage_config["Parameters"]["StageName"],
        "sagemaker:project-id": project_id,
        "sagemaker:project-name": args.sagemaker_project_name,
    }
    # Add tags from Project
    get_pipeline_custom_tags(args, sm_client, new_tags, project_arn)

    return {
        "Parameters": {**stage_config["Parameters"], **new_params},
        "Tags": {**stage_config.get("Tags", {}), **new_tags},
    }

def get_pipeline_custom_tags(args, sm_client, new_tags, project_arn):
    try:
        response = sm_client.list_tags(ResourceArn=project_arn)
        project_tags = response["Tags"]
        for project_tag in project_tags:
            new_tags[project_tag["Key"]] = project_tag["Value"]
    except Exception:
        logger.error("Error getting project tags")
    return new_tags

def get_cfn_style_config(stage_config):
    parameters = []
    for key, value in stage_config["Parameters"].items():
        parameter = {"ParameterKey": key, "ParameterValue": value}
        parameters.append(parameter)
    tags = []
    for key, value in stage_config["Tags"].items():
        tag = {"Key": key, "Value": value}
        tags.append(tag)
    return parameters, tags

def create_cfn_params_tags_file(config, export_params_file, export_tags_file):
    # Write Params and tags in separate file for Cfn cli command
    parameters, tags = get_cfn_style_config(config)
    with open(export_params_file, "w") as f:
        json.dump(parameters, f, indent=4)
    with open(export_tags_file, "w") as f:
        json.dump(tags, f, indent=4)

def create_sagemaker_image_uri(model_config, region):
    
    return sagemaker.image_uris.retrieve(
        region=region,
        framework=model_config.get("framework", None),
        image_scope="inference",
        model_id=model_config["model_id"],
        model_version=model_config["model_version"],
        instance_type=model_config["instance_type"]
    )

def load_model_config(stack_name):
    """Load model config from model_configs.json file
    """
    with open("model_configs.json", "r") as f:
        config = json.load(f)
    model_config = config.get(stack_name.replace('-', '_'))
    return model_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.environ.get("LOGLEVEL", "INFO").upper(),
    )
    parser.add_argument("--sagemaker-project-name", type=str, required=True)
    parser.add_argument("--dev-region", type=str, required=True)
    parser.add_argument("--region-deploy-us", type=str, required=True)
    parser.add_argument("--region-deploy-eu", type=str, required=True)
    parser.add_argument("--beta-role-arn", type=str, required=True)
    parser.add_argument("--prod-role-arn", type=str, required=True)
    parser.add_argument("--stack-name", type=str, required=True)
    parser.add_argument(
        "--model-package-group-name",
        type=str,
        required=False,
        help="default to ProjectName-ProjectId",
    )
    parser.add_argument(
        "--import-staging-config", type=str, default="staging-config.json"
    )
    parser.add_argument(
        "--import-prod-us-config", type=str, default="prod-us-config.json"
    )
    parser.add_argument(
        "--import-prod-eu-config", type=str, default="prod-eu-config.json"
    )
    parser.add_argument(
        "--export-staging-config",
        type=str,
        default="staging-config-export.json",
    )
    parser.add_argument(
        "--export-staging-params",
        type=str,
        default="staging-params-export.json",
    )
    parser.add_argument(
        "--export-staging-tags", type=str, default="staging-tags-export.json"
    )
    parser.add_argument(
        "--export-prod-us-config", type=str, default="prod-us-config-export.json"
    )
    parser.add_argument(
        "--export-prod-us-params", type=str, default="prod-us-params-export.json"
    )
    parser.add_argument(
        "--export-prod-us-tags", type=str, default="prod-us-tags-export.json"
    )
    parser.add_argument(
        "--export-prod-eu-config", type=str, default="prod-eu-config-export.json"
    )
    parser.add_argument(
        "--export-prod-eu-params", type=str, default="prod-eu-params-export.json"
    )
    parser.add_argument(
        "--export-prod-eu-tags", type=str, default="prod-eu-tags-export.json"
    )
    parser.add_argument("--export-cfn-params-tags", type=bool, default=False)
    args, _ = parser.parse_known_args()

    # Configure logging to output the line number and message
    log_format = "%(levelname)s: [%(filename)s:%(lineno)s] %(message)s"
    logging.basicConfig(format=log_format, level=args.log_level)

    # Create SageMaker client
    sm_client = boto3.client("sagemaker", region_name=args.dev_region)

    # Get SageMaker project info
    project_info = sm_client.describe_project(
        ProjectName=args.sagemaker_project_name
    )
    project_id = project_info["ProjectId"]
    project_arn = project_info["ProjectArn"]

    # Set Defaults
    if args.model_package_group_name:
        model_package_group_name = args.model_package_group_name
    else:
        model_package_group_name = (
            f"{args.sagemaker_project_name}-{project_id}"
        )

    model_config = load_model_config(args.stack_name)
    print(f"Model Data URL: {model_config['model_data_url']}")
    
    model_image_uri_us = create_sagemaker_image_uri(model_config, args.region_deploy_us)
    model_image_uri_eu = create_sagemaker_image_uri(model_config, args.region_deploy_eu)
    
    logger.info(f"**********Model Image URI - US*************: {model_image_uri_us}")
    logger.info(f"**********Model Image URI - EU*************: {model_image_uri_eu}")

    # Write the staging config
    with open(args.import_staging_config, "r") as f:
        staging_config = extend_config(
            args=args,
            sagemaker_image_uri=model_image_uri_us,
            model_config=model_config,
            stage_config=json.load(f),
            sm_client=sm_client,
            project_id=project_id,
            project_arn=project_arn,
            model_execution_role=args.beta_role_arn,
        )
    logger.debug(
        "Staging config: {}".format(json.dumps(staging_config, indent=4))
    )
    with open(args.export_staging_config, "w") as f:
        json.dump(staging_config, f, indent=4)
    if args.export_cfn_params_tags:
        create_cfn_params_tags_file(
            staging_config,
            args.export_staging_params,
            args.export_staging_tags,
        )

    # Write the prod US config for code pipeline
    with open(args.import_prod_us_config, "r") as f:
        prod_us_config = extend_config(
            args=args,
            sagemaker_image_uri=model_image_uri_us,
            model_config=model_config,
            stage_config=json.load(f),
            sm_client=sm_client,
            project_id=project_id,
            project_arn=project_arn,
            model_execution_role=args.prod_role_arn,
        )
    logger.debug("Prod US config: {}".format(json.dumps(prod_us_config, indent=4)))
    with open(args.export_prod_us_config, "w") as f:
        json.dump(prod_us_config, f, indent=4)
    if args.export_cfn_params_tags:
        create_cfn_params_tags_file(
            prod_us_config, args.export_prod_us_params, args.export_prod_us_tags
        )
    
    # Write the prod EU config for code pipeline
    with open(args.import_prod_eu_config, "r") as f:
        prod_eu_config = extend_config(
            args=args,
            sagemaker_image_uri=model_image_uri_eu,
            model_config=model_config,
            stage_config=json.load(f),
            sm_client=sm_client,
            project_id=project_id,
            project_arn=project_arn,
            model_execution_role=args.prod_role_arn,
        )
    logger.debug("Prod EU config: {}".format(json.dumps(prod_eu_config, indent=4)))
    with open(args.export_prod_eu_config, "w") as f:
        json.dump(prod_eu_config, f, indent=4)
    if args.export_cfn_params_tags:
        create_cfn_params_tags_file(
            prod_eu_config, args.export_prod_eu_params, args.export_prod_eu_tags
        )