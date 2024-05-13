# Test harness for LLM's

This repository contains code and data essential for constructing a `test harness`, and streamlining the evaluation of ML approaches by standardizing input processing, model execution, and outcome analysis with uniform metrics.

## Folders

- **llm-sagermaker**: Contains Jupyter notebooks for evaluation.
- **Utils**: Contains utility scripts or modules used by the project.
- **Data**: Contains datasets and other data files used in the project.
- **Prompts**: Contains prompts used for evaluation or testing.

## Pre-requisites
    1. The test data is cleaned, uploaded into s3 for quick evaluation:
        s3 URI: s3://sagemaker-sigparser-caylent-mlops/data/email-type/input/processed/
    2. The prompt is created in the prompts/email-type.py
    3. The endpoint is deployed in sagemaker for inference.
    4. Make sure to initialize all the pre-requisites in the jupyter notebook section: Pre-requisites.


## Jupyter Notebook

The Jupyter notebook provided in the `llm-sagemaker` folder expects cleaned CSV data for quick evaluation and testing. It also uses prompts configured from the `Prompts` folder.

## Input Data

The input data required for evaluation and testing should be uploaded to the s3 URI: s3://sagemaker-sigparser-caylent-mlops/data/email-type/input/processed/

## Holdout dataset 

A sub-sample of records is configurable in theJupyter notebook for quick testing and evaluation. This will help to quickly test the prompt for few records. By default, the records count is set to holdout dataset size.

## Evaluation

The evaluation process is automatically calculated within the Jupyter notebook, and the results are presented at the end of the notebook.

## Output Files

Evaluation results, along with the prediction results are saved in the s3 based on the model used:
    s3 URI: s3://sagemaker-sigparser-caylent-mlops/data/email-type/output/Llama 2 7B Chat/

## To-Do
- Expand the code to handle additional use cases.
