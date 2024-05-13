# Project Statement
This project focuses on the binary classification of email data into two categories: 'Person' and 'Non-Person', utilizing the DistilBERT model, which offers a leaner and faster alternative for natural language processing tasks.


# Usage
To run the data cleaning process, open the Jupyter notebook distilBERT_data_cleaning.ipynb and execute the cells.
For training the model, use the notebook distilBERT_training.ipynb.
Finally, for evaluation, use the distilBERT_evaluation.ipynb notebook.


# Workflow
https://docs.google.com/document/d/1s1tG_7ETGNXaCMUVvQSc68n6WUQ9fZxED3H77u5ssOo/edit#bookmark=id.hs3zyw5fu5lb


# File Descriptions
distilBERT_data_cleaning.ipynb: Performs data cleaning and preparation of the training and test datasets.
distilBERT_training.ipynb: Contains code to fine-tune the DistilBERT model with the processed training dataset.
distilBERT_evaluation.ipynb: Evaluates the model on a test set, creates an endpoint, and computes performance metrics.
distilBERT_utility.py: A utility module containing functions used across the project for data handling, querying the endpoint, and calculating metrics.


# Requirements
The project requires the following Python libraries:
AWS SageMaker Integration: boto3, sagemaker
Data Handling and Computation: pandas, numpy
Progress Monitoring: tqdm
Model Evaluation Metrics: sklearn
Visualization: matplotlib, seaborn
File Handling and System Operations: io, os, tarfile, datetime, time, json
SageMaker Specific Tools: sagemaker.session, sagemaker.jumpstart.model, sagemaker.jumpstart.estimator, sagemaker.tuner, sagemaker.predictor


# Endpoint Creation and Testing
Refer to distilBERT_evaluation.ipynb for detailed steps on creating and deploying the model as an endpoint on AWS SageMaker and testing it with your dataset.


# License
[MIT](https://choosealicense.com/licenses/mit/)