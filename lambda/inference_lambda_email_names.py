import json
import boto3
import logging
import re
import os
import time

sagemaker_runtime = boto3.client('sagemaker-runtime')

def extract_names(response):
    """
    Checks the email names from the result generated by the Mistral model.

    Args:
    - response (list): The result generated by the Mistral model.

    Returns:
    - dict: A dictionary containing the email names
    """
    try:
        # extract generated text from response
        result = response[0]["generated_text"]
        print(f"LLM response: {result}")

        # Initialize names dictionary with default values
        names = {
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "name_prefix": "",
            "name_suffix": ""
        }

        # Regular expression pattern to match each component
        patterns = {
            "first_name": r"First Name: ([^\n]*)",
            "middle_name": r"Middle Name: ([^\n]*)",
            "last_name": r"Last Name: ([^\n]*)",
            "name_prefix": r"Name Prefix: ([^\n]*)",
            "name_suffix": r"Name Suffix: ([^\n]*)"
        }

        # Extract each component from the result
        for key, pattern in patterns.items():
            match = re.search(pattern, result)
            if match:
                names[key] = match.group(1)

    except Exception as e:
        print("Error occurred during result extraction:", e)
        names["Remarks"] = f'{type(e)}: {str(e)}'

    return names

def get_context(email_address, display_name):
    """
    Generate the context string for the email name extraction prompt.

    Args:
    - email_address (str): The email address.
    - display_name (str): The display name associated with the email address.

    Returns:
    - str: The context string containing the input data.
    """
    email_address = email_address.strip()
    display_name = display_name.strip()
    
    context_input_str = f"""Input:"""
    context_data = f"""{{"Email Address": "{email_address}", "Display Name": "{display_name}"}}"""
    context = context_input_str.strip() + context_data.strip()
    
    return context

def get_prompt():
    """
    Generate the prompt for extracting email name components.

    Returns:
    - dict: A dictionary containing the prompt information.
    """
    prompt_email_names = {}
    prompt_type = "email-names"
    system_prompt = '''You are a highly skilled assistant specializing in data extraction. Your current task is to analyze the 'Email Address' and 'Display Name' fields to extract the 'First Name', 'Middle Name', 'Last Name', 'Name Prefix', and 'Name Suffix'.
    
    Please respond strictly with this JSON format:
    {
      "First Name": "xxx", 
      "Middle Name": "xxx", 
      "Last Name": "xxx", 
      "Name Prefix": "xxx", 
      "Name Suffix": "xxx"
    }
    
    where 'xxx' should be replaced with the corresponding name component extracted from the 'Email Address' or 'Display Name' fields. If a component is not present, leave the value as an empty string "".
    
    Name components are generally extracted from the 'Display Name' field, however, reviewing the 'Email Address' field can give additional information into the correct extraction of the 'First Name', 'Middle Name', and 'Last Name' fields.
    
    The 'Display Name' field can include extra terms like business names, job codes, locations, email addresses, and more. All of these extra terms should be ignored and not extracted as one of the name components.
    
    Here are three examples of how to correctly extract name components from an 'Email Address' and 'Display Name':
    
    Input:
    {
        "Email Address": " john.doe@gmail.com,
        "Display Name": “Dr. John Alex Doe Jr"
    }

    Output:

    {
        "First Name": “J”John,
        "Middle Name": “Alex”,
        "Last Name": “Doe”,
        "Name Prefix": “Dr”,
        "Name Suffix": “Jr”
    }

    Input:
    {
        "Email Address": "david.brown@gmail.com",
        "Display Name": "David Robert Brown Jr.”
    }

    Output:
    {
        "First Name": "David",
        "Middle Name": "Robert",
        "Last Name": "Brown",
        "Name Prefix": "",
        "Name Suffix": "Jr."
    }

    Input:
    {
        "Email Address": “emma.smith@gmail.com",
        "Display Name": "Dr. Emma Grace Smith III"
    }

    Output:
    {
        "First Name": "Emma",
        "Middle Name": "Grace",
        "Last Name": "Smith",
        "Name Prefix": "Dr.",
        "Name Suffix": "III"
    }
    '''
    
    instruction = f"""Please extract the email name components from the following input. All output must be in valid JSON. Don’t add explanation beyond the JSON."""
    
    prompt_email_names = {
        "prompt_type": prompt_type,
        "system_prompt": system_prompt,
        "instruction": instruction
    }
    return prompt_email_names


def lambda_handler(event, context):
    """
    Checks the email names from the result generated by the Mistral model.

    Args:
    - response (list): The result generated by the Mistral model.

    Returns:
    - dict: A dictionary containing the email names
    """
    start_time = time.time()
    endpoint_name = os.environ.get("ENDPOINT_NAME", "sagemaker-sigparser-llmops-staging-email-names")

    body = ""
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        return {"status": "bad request"}
    
    email_address = body["email_address"]
    display_name = body["email_display_name"]
    print("Request received email_address: %s, display_name: %s", email_address, display_name)

    prompt_obj = get_prompt()
    system_prompt = prompt_obj["system_prompt"]
    instruction = prompt_obj["instruction"]
    context = get_context(email_address, display_name)

    template = {
        "prompt": "{system_prompt}\n\n### Instruction:\n{instruction}\n\n### Input:\n{context}"
    }

    # populate prompt template
    input_output_demarkation_key = "\n\n### Response:\n"
    prompt = template["prompt"].format(
            system_prompt=system_prompt, instruction=instruction, context=context
        )

    # prepare payload
    payload = {
        "inputs": prompt
        + input_output_demarkation_key,
        "parameters": {"max_new_tokens": 100, "temperature":0.1, 'top_p':0.1},
    }

    pre_invoke_time = time.time()
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=json.dumps(payload),
        CustomAttributes="accept_eula=true",
    )
    
    post_invoke_time = time.time()
    print(f"SageMaker invocation duration: {post_invoke_time - pre_invoke_time} seconds")
    # Read and decode the response body
    response_body = response["Body"].read().decode("utf8")

    # Parse the JSON response
    response = json.loads(response_body)
    
    pre_extraction_time = time.time()
    # extract results
    names = extract_names(response)
    
    post_extraction_time = time.time()
    print(f"Name extraction duration: {post_extraction_time - pre_extraction_time} seconds")
    
    result = {
        "extracted_names": names,
        "input_data":{
            "email_address": email_address,
            "email_display_name": display_name
        }
    }

    logging.info("Response received: %s", response_body)
    
    end_time = time.time()
    print(f"Total Lambda handler duration: {end_time - start_time} seconds")
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

