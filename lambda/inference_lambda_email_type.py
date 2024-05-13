import boto3
import json
import os
import logging

def lambda_handler(event, context):
    #TODO: update the endpoint name for staging and production as needed
    endpoint_name = os.environ.get("ENDPOINT_NAME", "sagemaker-sigparser-llmops-staging-email-type")
    runtime = boto3.client('runtime.sagemaker')
    #Getting payload from API endpoint
    body = ""
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        return {"status": "bad request"}
    
    input_str = ', '.join([body["email_address"], body["email_name"], body["email_display_name"]])

    logging.info("Request received input_str: %s", input_str)
    
    #Calling SageMaker endpoint
    #add try catch block for the below
    try:
        response = runtime.invoke_endpoint(EndpointName=endpoint_name,
                                            ContentType='text/csv',
                                            Body=input_str)
        
    except Exception as e:
        print("Error invoking SageMaker endpoint:", e)
        return {"status": "error"}
    
    prediction = ""
    result = json.loads(response['Body'].read().decode())
    
    prediction_result = [{
        "input_string": item["sentence"],
        "probabilities": {
            "person": item["probabilities"][0],
            "non_person": item["probabilities"][1]
        }
    } for item in result]
    
    #Parsing result
    probabilities = result[0]['probabilities']
    person = probabilities[0]
    nonperson = probabilities[1]
    
    if nonperson > 0.9:
        prediction = 'Non-Person'
    else:
        prediction = 'Person'
        

    #Return result to API
    response =     {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            "pred_email_type": prediction,
            "response": prediction_result
        })
    }
    logging.info("API response: %s", response)
    return response