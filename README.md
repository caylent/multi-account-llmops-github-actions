## Overview

This GitHub repository contains the source code and resources for  deploying DistilBERT and Mistral-7B models. The project is designed to work seamlessly with AWS SageMaker, providing end-to-end solutions from data preparation to deployment.

## Toolchain

- **Development Environment**: Amazon SageMaker Studio Notebooks
- **Models**:
  - **Classification usecase**: HuggingFace/DistilBERT
  - **Entity Extraction usecase**: SageMaker Jumpstart/Mistral-7B
- **Compute**: Amazon SageMaker Instances, AWS Lambda
- **Infrastructure as Code (IaC)**: AWS CloudFormation
- **Deployment**: GitHub Actions Workflows

For more information on enabling CI/CD for multi-region Amazon SageMaker endpoints, please refer to the following AWS blog post: [Enable CI/CD of Multi-Region Amazon SageMaker Endpoints](https://aws.amazon.com/blogs/machine-learning/enable-ci-cd-of-multi-region-amazon-sagemaker-endpoints/)

## Repository Structure
```
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── api_load_tests
├── build_deployment_configs.py
├── copy_lambda_and_model_artifacts.py
├── deploy_stack.py
├── endpoint-config-template.yml
├── lambda
│   ├── inference_lambda_email_names.py
│   └── inference_lambda_email_type.py
├── model_configs.json
├── project
├── utils
├── prod-eu-config.json
├── prod-us-config.json
├── setup.cfg
├── setup.py
├── staging-config.json
└── tox.ini
```

### Key components

- `.github`: Contains GitHub Actions scripts for CI/CD pipelines, automating the build and deployment of models.
- `lambda`: Contains AWS Lambda functions for handling API requests, integrating with API Gateway to process and respond to model inference calls.
- `utils`: Functions for evaluating the performance of your predictions. Find more details [here](utils/README.md)
- `api-loadtest`: Contains all the load test scripts for endpoint invocation configured through locust. Find more details [here](api_load_tests/README.md)

## Prerequisites

AWS SageMaker Studio IDE, IAM permissions for accessing SageMaker resources, S3 buckets, Lambda functions, and managing CloudWatch, Python 3.x environment with necessary libraries installed.

### Key Modules and Libraries

Before initiating the project, ensure the following packages are installed:
    -boto3 for AWS SDK
    -sagemaker Python SDK for interacting with SageMaker
    -pandas, numpy for data manipulation
    -transformers from Hugging Face for model implementations

## Deploy your model

This code repository demonstrates how you can organize your code for deploying an realtime inference Endpoint infrastructure. This code repository is created as part of creating a Project in SageMaker. 

This code repository defines the CloudFormation template which defines the Endpoints as infrastructure. It also has configuration files associated with `StagingDeploy`,  `ProductionDeployUS` and `ProductionDeployEU` stages.

Upon triggering a deployment, the GitHub Actions workflow will deploy three endpoints in the `StagingDeploy`, `ProductionDeployUS`, and `ProductionDeployEU` environments. 

After the first deployment at `StagingDeploy` is completed, the GitHub Actions workflow waits for a manual approval step for promotion to the production stage.

You own this code and you can modify this template to change as you need it, add additional tests for your custom validation. 

A description of some of the artifacts is provided below:
The GitHub Actions workflow to build and deploy Endpoints.

```
.github/workflows/deploy.yml
```

```
model_configs.json
```
This JSON file contains code to retrieve the latest approved model S3 path and export staging and configuration files. It is invoked from the deploy stage. 

Make sure to update the `DeploymentVersion` and the `model_data_url` for each deployment.

Optionally, you can update the configuration for autoscaling for each model during the deployment.

`endpoint-config-template.yml`
 - this CloudFormation template file is packaged by the build step in the GitHub Actions workflow and is deployed in different stages.

`staging-config.json`
 - this configuration file is used to customize `staging` stage in the pipeline. You can configure the instance type, instance count here.
`prod-us-config.json`
 - this configuration file is used to customize `prod` stage in the pipeline. You can configure the instance type, instance count here.

`prod-eu-config.json`
 - this configuration file is used to customize `prod` stage in the pipeline. You can configure the instance type, instance count here.

