import json
import boto3
import re
import time




### UTILITY FUNCTIONS ###

def timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.5f} seconds to execute.")
        return result
    return wrapper


class LlamaChatV1():
    def __init__(self, endpoint_name):
        self.sagemaker_client = boto3.client("sagemaker-runtime")
        self.endpoint_name = endpoint_name
    
    @timing
    def query_llama_endpoint(self, payload):
        """
        Invoke the SageMaker endpoint with the provided payload.

        Parameters:
            payload (dict): The payload data to be sent to the endpoint.

        Returns:
            dict: The JSON response from the endpoint.

        Raises:
            botocore.exceptions.ClientError: If an error occurs during the invocation.
        """
        try:
            # Invoke the SageMaker endpoint
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType="application/json",
                Body=json.dumps(payload),
                CustomAttributes="accept_eula=true",
            )

            # Read and decode the response body
            response_body = response["Body"].read().decode("utf8")

            # Parse the JSON response
            json_response = json.loads(response_body)

            return json_response

        except botocore.exceptions.ClientError as e:
            # Handle the botocore client error
            print("Error invoking endpoint:", e)
            raise e  # Re-raise the exception to propagate the error further
        
    @timing    
    def check_email_type(self, response):
        """
        Checks the email type from the result generated by the model.

        Args:
        - result (list): The result generated by the model.

        Returns:
        - dict: A dictionary containing the email type.
        """
        try:
            # Extract generated text from response
            result = response[0]["generated_text"]

            # Search for email_address_type in the generated text using regex
            match = re.search(r'"email_address_type":\s*"([^"]+)"', result)

            # Initialize output dictionary
            output_dict = {"p_email_type": ""}

            # Process match if found
            if match:
                email_address_type = match.group(1)
                # Map email_address_type to 'Person' or 'Non-Person'
                if email_address_type == 'person':
                    output_dict["p_email_type"] = "Person"
                elif email_address_type == 'non-person':
                    output_dict["p_email_type"] = "Non-Person"

            return output_dict

        except Exception as e:
            print("Error occurred during result extraction:", e)
            # Handle the error as per the requirement
            return {"p_email_type": ""}

    @timing    
    def extract_results(self, response, task_type):
        """
        Handle the response based on the task type.

        Parameters:
            task_type (str): The type of task.
            response (dict): The response data.

        Returns:
            dict: The processed result.

        """
        try:
            result = {}
            if task_type == "email-type":
                result = self.check_email_type(response)
            return result

        except Exception as e:
            print("Error handling response:", e)
            # Handle the error as per the requirement
            return None


    @timing
    def get_results(self, row):
        """
        Get results based on the provided row data.

        Parameters:
            row (tuple): A tuple containing the row data.

        Returns:
            dict or None: A dictionary containing the extracted results or None if an error occurs.

        Raises:
            KeyError: If one or more expected keys are not found in the row.
        """

        # columns
        # Prompt
        # Email Address
        # Email Address Name
        # Email Address Display Name
        # Email Type

        try:
            # Validate presence of expected keys
            if 'system_prompt' not in row[1] or 'instruction' not in row[1] or 'prompt_type' not in row[1]:
                raise KeyError("One or more expected keys not found in row")

            # Extract data from row[1]
            system_prompt = row[1]['system_prompt']
            instruction = row[1]['instruction']
            prompt_type = row[1]['prompt_type']

            # Define base prompt template
            base_prompt = "<s>[INST]\n<<SYS>>\n{system_prompt}\n<</SYS>>\n\n{instruction}[/INST]"

            # Populate prompt template
            prompt_template = {
                "prompt": base_prompt
            }

            # Generate dialog
            dialog = prompt_template["prompt"].format(
                system_prompt=system_prompt,
                instruction=instruction
            )

            # Prepare payload
            payload = {
                "inputs": dialog,
                "parameters": {"max_new_tokens": 256, "top_p": 0.9, "temperature": 0.2}
            }

            # Query LLAMA endpoint
            response = self.query_llama_endpoint(payload)

            # Extract results
            result = self.extract_results(response, prompt_type)

            return result

        except KeyError as e:
            print("Error processing row:", e)
            # Handle the error as per the requirement
            return None

        except Exception as e:
            print("Unexpected error occurred:", e)
            # Handle the error as per the requirement
            return None



class Mistral_7B_V1():
    def __init__(self, endpoint_name):
        self.sagemaker_client = boto3.client("sagemaker-runtime")
        self.endpoint_name = endpoint_name
    
    @timing
    def query_mistral_endpoint(self, payload):
        """
        Invoke the SageMaker endpoint with the provided payload.

        Parameters:
            payload (dict): The payload data to be sent to the endpoint.

        Returns:
            dict: The JSON response from the endpoint.

        Raises:
            botocore.exceptions.ClientError: If an error occurs during the invocation.
        """
        try:
            # Invoke the SageMaker endpoint
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType="application/json",
                Body=json.dumps(payload),
                CustomAttributes="accept_eula=true",
            )

            # Read and decode the response body
            response_body = response["Body"].read().decode("utf8")

            # Parse the JSON response
            json_response = json.loads(response_body)

            return json_response

        except botocore.exceptions.ClientError as e:
            # Handle the botocore client error
            print("Error invoking endpoint:", e)
            raise e  # Re-raise the exception to propagate the error further
        
    @timing    
    def check_email_type(self, response):
        """
        Checks the email type from the result generated by the model.

        Args:
        - result (list): The result generated by the model.

        Returns:
        - dict: A dictionary containing the email type.
        """
        try:
            # Extract generated text from response
            result = response[0]["generated_text"]

            # Search for email_address_type in the generated text using regex
            match = re.search(r'"email_address_type":\s*"([^"]+)"', result)

            # Initialize output dictionary
            output_dict = {"p_email_type": ""}

            # Process match if found
            if match:
                email_address_type = match.group(1)
                # Map email_address_type to 'Person' or 'Non-Person'
                if email_address_type == 'person':
                    output_dict["p_email_type"] = "Person"
                elif email_address_type == 'non-person':
                    output_dict["p_email_type"] = "Non-Person"

            return output_dict

        except Exception as e:
            print("Error occurred during result extraction:", e)
            # Handle the error as per the requirement
            return {"p_email_type": ""}

    @timing    
    def extract_results(self, response, task_type):
        """
        Handle the response based on the task type.

        Parameters:
            task_type (str): The type of task.
            response (dict): The response data.

        Returns:
            dict: The processed result.

        """
        try:
            result = {}
            if task_type == "email-type":
                result = self.check_email_type(response)
            return result

        except Exception as e:
            print("Error handling response:", e)
            # Handle the error as per the requirement
            return None


    @timing
    def get_results(self, row):
        """
        Get results based on the provided row data.

        Parameters:
            row (tuple): A tuple containing the row data.

        Returns:
            dict or None: A dictionary containing the extracted results or None if an error occurs.

        Raises:
            KeyError: If one or more expected keys are not found in the row.
        """

        # columns
        # Prompt
        # Email Address
        # Email Address Name
        # Email Address Display Name
        # Email Type

        try:
            # Validate presence of expected keys
            if 'system_prompt' not in row[1] or 'instruction' not in row[1] or 'context' not in row[1] or 'prompt_type' not in row[1]:
                raise KeyError("One or more expected keys not found in row")

            # Extract data from row[1]
            system_prompt = row[1]['system_prompt']
            instruction = row[1]['instruction']
            context = row[1]['context']
            prompt_type = row[1]['prompt_type']

            # Define base prompt template
            template = {
                "prompt": "{system_prompt}\n\n### Instruction:\n{instruction}\n\n### Input:\n{context}"
            }
            # with open("../data/prompts/mistral-7b/template.json", "w") as f:
            #     json.dump(template, f)

            # Populate prompt template
            input_output_demarkation_key = "\n\n### Response:\n"
            prompt = template["prompt"].format(
                    system_prompt=system_prompt, instruction=instruction, context=context
                )

            # Prepare payload
            payload = {
                "inputs": prompt
                + input_output_demarkation_key,
                "parameters": {"max_new_tokens": 100, "temperature":0.2, 'top_p':0.1},
            }

            # Query LLAMA endpoint
            response = self.query_mistral_endpoint(payload)

            # Extract results
            result = self.extract_results(response, prompt_type)

            return result

        except KeyError as e:
            print("Error processing row:", e)
            # Handle the error as per the requirement
            return None

        except Exception as e:
            print("Unexpected error occurred:", e)
            # Handle the error as per the requirement
            return None