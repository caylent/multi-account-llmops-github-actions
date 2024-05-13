#This utility file contains functions to query the endpoint, get predictions for a test dataset, and calculate metrics as needed. 

#Importing necessary packages and libraries
import sagemaker, boto3
import pandas as pd
import numpy as np
from tqdm import tqdm

from sagemaker.session import Session
from sagemaker.jumpstart.model import JumpStartModel
from sagemaker import image_uris, model_uris, script_uris, hyperparameters
from sagemaker.jumpstart.estimator import JumpStartEstimator, Estimator
from sagemaker.tuner import HyperparameterTuner
from sagemaker.tuner import ContinuousParameter
from sagemaker.predictor import Predictor
from sagemaker import TrainingJobAnalytics
from io import StringIO, BytesIO

from sklearn.metrics import precision_score, recall_score, accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score

import seaborn as sns
import matplotlib.pyplot as plt

import json
import time
import datetime
import tarfile
import os

pd.options.display.max_colwidth = 500

s3_client = boto3.client('s3')

#Function to retrieve a file from S3 and read as csv file
def retrieve_from_s3(bucket_name, file_key):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code == 200:
        return pd.read_csv(response['Body'])
    else:
        raise Exception(f"Failed to retrieve the CSV file: HTTP {status_code}")
        
#Function to save csv to S3 bucket
def save_to_s3(df, bucket_name, file_key, mode):
    csv_buffer = StringIO()
    if mode=="train":
        #IMPORTANT: The train data should not contain a header
        df.to_csv(csv_buffer, index=False, header=False)
    else: 
        df.to_csv(csv_buffer, index=False)
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=csv_buffer.getvalue())
    except Exception as e:
        raise Exception(f"Failed to upload csv file to S3 bucket: {str(e)}")

#Function to save json file to S3 bucket
def save_json_to_s3(data, bucket_name, file_key):
    json_buffer = StringIO()
    json.dump(data, json_buffer) 
    json_buffer.seek(0) 
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=json_buffer.getvalue())
        print("The JSON file has been uploaded successfully to the S3 bucket.")
    except Exception as e:
        raise Exception(f"Failed to upload JSON file to S3: {str(e)}")

#Function to load test set and ground truth labels
def test_dataset(bucket_name, test_file_key, gt_file_key):
    test_df = retrieve_from_s3(bucket_name, test_file_key)
    test_list = test_df['combined'].tolist()
    
    gt_df = retrieve_from_s3(bucket_name, gt_file_key)
    gt_values = gt_df['gt'].tolist()
    
    #gt = ['LABEL_0' if x == 0 else 'LABEL_1' for x in gt_values]
    #'LABEL_0' is for Person and 'LABEL_1' is for Non-Person
    return test_list, gt_values

#Function to convert Email Type str values to numeric values
def email_type_to_int(email_type):
    return 0 if email_type == "Person" else 1

#Function to check if there are any NaN values and replacing with "" values
def nan_values(df):
    if df.isna().any().any():
        df.fillna("", inplace=True)
    '''
    #Creating a mask where all values in a row are NaN
    mask = train_df.isna().any(axis=1)
    nan_rows_df = train_df[mask]
    '''

#Function to create an endpoint configuration and endpoint
def create_endpoint(instance_type, endpoint_name, model_data, aws_role):
    print("Model data location given: ", model_data)
    model_id = 'huggingface-tc-distilbert-base-multilingual-cased'
    model_version = '*'
    
    #Retrieve the inference docker container uri
    deploy_image_uri = image_uris.retrieve(
        region=None,
        framework=None,
        image_scope="inference",
        model_id=model_id,
        model_version=model_version,
        instance_type=instance_type,
    )
    #Retrieve the inference script uri
    deploy_source_uri = script_uris.retrieve(
        model_id=model_id, model_version=model_version, script_scope="inference"
    )

    #Create a SageMaker Model object
    model = sagemaker.model.Model(
        model_data=model_data,
        role=aws_role,
        image_uri=deploy_image_uri,
        source_dir=deploy_source_uri,
        entry_point="inference.py",  
    )

    #Deploy the model on an ml.m5.xlarge instance
    finetuned_predictor = model.deploy(
        initial_instance_count=1,
        instance_type=instance_type,
        endpoint_name=endpoint_name,
    )

#Function to query the endpoint
def query_endpoint(finetuned_predictor, encoded_text):
    response = finetuned_predictor.predict(
        encoded_text, {"ContentType": "application/x-text", "Accept": "application/json;verbose"}
    )
    if isinstance(response, bytes):
        response = response.decode('utf-8')
    return response

#Function to parse predictions from the model's response
def parse_response(model_predictions_str):
    model_predictions = json.loads(model_predictions_str)
    probabilities, labels, predicted_label = (
        model_predictions["probabilities"],
        model_predictions["labels"],
        model_predictions["predicted_label"],
    )
    return probabilities, labels, predicted_label
        
#Function to calculate precision, recall, f1 score, accuracy
def classification_metrics(gt, predictions):
    report = classification_report(gt, predictions, target_names=['LABEL_0', 'LABEL_1'], output_dict=True)

    precision_label_0 = report['LABEL_0']['precision']
    recall_label_0 = report['LABEL_0']['recall']

    precision_label_1 = report['LABEL_1']['precision']
    recall_label_1 = report['LABEL_1']['recall']

    precision = precision_score(gt, predictions, average='macro')  #Overall Precision
    recall = recall_score(gt, predictions, average='macro')  #Overall Recall
    overall_accuracy = report['accuracy'] #Overall Accuracy

    numeric_predictions = np.array([0 if x == 'LABEL_0' else 1 for x in predictions])
    numeric_ground_truth = np.array([0 if x == 'LABEL_0' else 1 for x in gt])
    
    f1 = f1_score(numeric_ground_truth, numeric_predictions, average='macro') #F1 score

    print(f"Precision for Person: {precision_label_0}")
    print(f"Recall for Person: {recall_label_0}\n")

    print(f"Precision for Non-Person: {precision_label_1}")
    print(f"Recall for Non-Person: {recall_label_1}\n")

    print(f"Overall Precision: {precision}")
    print(f"Overall Recall: {recall}")
    print(f"F1 Score: {f1}\n")
    print(f"Overall Accuracy: {overall_accuracy}")
    
    return numeric_predictions, numeric_ground_truth, overall_accuracy, precision, recall, f1


#Function to print confusion matrix, f1 score and class wise accuracy
def confusion_matrix_accuracy(numeric_ground_truth, numeric_predictions):
    #Calculate confusion matrix
    conf_matrix = confusion_matrix(numeric_ground_truth, numeric_predictions)
    print(conf_matrix)
    TN, FP, FN, TP = conf_matrix.ravel()
    person_accuracy = (TN / (TN + FP)) * 100  # Accuracy for "Person"
    non_person_accuracy = (TP / (TP + FN)) * 100      # Accuracy for "Non-Person"
    print(f"\nAccuracy for Person: {person_accuracy:.2f}%")
    print(f"Accuracy for Non-Person: {non_person_accuracy:.2f}%")
    
    return conf_matrix

#Function to plot heatmap from confusion matrix
def plot_heatmap(conf_matrix):
    total = conf_matrix.sum()
    percentages = conf_matrix / total * 100

    labels = np.array([["True Negative", "False Positive"], ["False Negative", "True Positive"]])
    annot = np.array([["{0}\n{1:.2f}%\n{2}".format(num, perc, label)
                       for num, perc, label in zip(conf_matrix.flatten(),
                                                    percentages.flatten(),
                                                    labels.flatten())]]).reshape(2,2)

    #Plotting the heatmap
    plt.figure(figsize=(10, 7))
    sns.heatmap(conf_matrix, annot=annot, fmt="", cmap="Blues", cbar=True, 
                xticklabels=['Person', 'Non-Person'], yticklabels=['Person', 'Non-Person'])
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')
    plt.title('Confusion Matrix Heatmap')
    plt.show()

#Function to print the percentage of total records correctly classified and incorrectly classified according to label
def percentage_records_classified(conf_matrix):
    TN, FP, FN, TP = conf_matrix.ravel()

    total_records = np.sum(conf_matrix)
    correctly_classified_percentage = (TP + TN) / total_records * 100
    wrongly_classified_as_0_percentage = FN / total_records * 100
    wrongly_classified_as_1_percentage = FP / total_records * 100

    print(f"Percentage of the total records correctly classified: {correctly_classified_percentage:.2f}%")
    print(f"Percentage of the total records wrongly classified as 'Person' when the True(actual) label is 'Non-Person': {wrongly_classified_as_0_percentage:.2f}%")
    print(f"Percentage of the overall data wrongly classified as 'Non-Person' when the True(actual) label is 'Person': {wrongly_classified_as_1_percentage:.2f}%")
    
#Function to filter misclassified predictions and save as .csv file
def misclassified_pred(all_predictions_df, bucket_name, file_key):
    misclassified_df = all_predictions_df[all_predictions_df['True Label'] != all_predictions_df['Predicted Label']]
    save_to_s3(misclassified_df, bucket_name, file_key, mode="test")

#Function to save all predictions along with their confidence values to a csv file and save in S3 bucket
def save_predictions(test_list, gt, predictions, probabilities_person, probabilities_non_person, bucket_name, file_key):
    label_map = {'LABEL_0': 'Person', 'LABEL_1': 'Non-Person'} 
    all_data_dicts = []

    for text, true_label, predicted_label, prob_person, prob_non_person in zip(test_list, gt, predictions, probabilities_person, probabilities_non_person):

        true_label_mapped = label_map.get(true_label, true_label)
        predicted_label_mapped = label_map.get(predicted_label, predicted_label)

        data_dict = {
            "Text": text,
            "True Label": true_label_mapped,
            "Predicted Label": predicted_label_mapped,
            "Probability for Person": round(prob_person, 4),
            "Probability for Non-Person": round(prob_non_person, 4)
        }
        all_data_dicts.append(data_dict)

    all_data_df = pd.DataFrame(all_data_dicts)
    text_columns = all_data_df['Text'].str.split(',', expand=True)
    
    text_columns.columns = [f'Text_Part_{i}' for i in range(text_columns.shape[1])]
    final_df = pd.concat([text_columns, all_data_df.drop(columns=['Text'])], axis=1)
    final_df.columns.values[0:3] = ['Email Address', 'Email Address Name', 'Email Address Display Name']
    desired_column_order = ['Email Address', 'Email Address Name', 'Email Address Display Name',
                            'True Label', 'Predicted Label', "Probability for Person", "Probability for Non-Person"]
    
    final_df = final_df[desired_column_order]
    save_to_s3(final_df, bucket_name, file_key, mode="test")
    
    return final_df
    