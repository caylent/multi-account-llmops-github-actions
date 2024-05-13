"""
This script is used to create a locust load test for the email API. It reads the email data from a CSV file and the API configurations from a JSON file. 
It then creates a locust user class for each configuration and runs the load test based on the configurations.
"""

from locust import HttpUser, task, between, events
import os
import json
import pandas as pd
import time
import datetime
import sys
import itertools

# Load email data from CSV
input_data_prefix = 'api_load_tests/data/inputs'
output_data_prefix = 'api_load_tests/data/outputs'
email_data = pd.read_csv(f'{input_data_prefix}/sp_llm_emailname_load_testing.csv').to_dict('records')

# Load configuration from JSON
with open('api_load_tests/api_configs.json', 'r') as f:
    config = json.load(f)

# Base class with common configurations
class BaseEmailUser(HttpUser):
    wait_time = between(1, 2)
    api_key = os.getenv('API_KEY')
    abstract = True

    def headers(self):
        return {'Content-Type': 'application/json', 'x-api-key': self.api_key}

# List to store response data
responses = []

# Start time
start_time = time.time()

# track the number of requests
num_requests = 0

# Dynamically create user classes based on configuration
def create_user_class(class_name, details):
    class NewUser(BaseEmailUser):
        host = details['host']
        path = details['path']
        payload_structure = details['payload']
        # uncomment the line below if you want to stop the test when all data is processed
        data = iter(email_data) # Create an iterator for the email data
        # uncomment the line below if you want to cycle through the data indefinitely
        #data = itertools.cycle(email_data)

        @task
        def post_data(self):
            global num_requests
            try:
                data_point = next(self.data)  # For now, we will raise StopIteration when data ends
            except StopIteration:
                total_time = time.time() - start_time
                print(f"All {len(email_data)} records have been processed in {total_time:.2f} seconds.")               
                
                # Writing responses to file once all data has been processed
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                with open(f"{output_data_prefix}/responses_{timestamp}.json", "w") as f:
                    json.dump(responses, f, indent=4)
                
                # capture command line arguments
                cmd_args = " ".join(sys.argv[1:])
                
                # Also write command line arguments and summary to file
                with open(f"{output_data_prefix}/summary_{timestamp}.txt", "w") as f:
                    f.write(f"User class: {class_name}\n")
                    f.write(f"Host: {self.host}\n")
                    f.write(f"Path: {self.path}\n")
                    f.write(f"Total number of records: {len(email_data)}\n")
                    f.write(f"Total number of requests: {num_requests}\n")
                    f.write(f"Total time taken: {total_time:.2f} seconds\n")
                    f.write(f"Command line arguments: {cmd_args}\n")
                    
                self.environment.runner.quit()
                return

            # Prepare the data to be sent in the POST request
            data_to_post = {key: data_point[key] for key in self.payload_structure.keys()}
            with self.client.post(self.path, json=data_to_post, headers=self.headers(), catch_response=True) as response:
                if response.ok:
                    response_data = response.json()
                    responses.append(response_data)
                else:
                    # Cases where the response is not OK
                    response.failure("Got wrong response!")
                    
            num_requests += 1

    NewUser.__name__ = class_name
    return NewUser

# Create user classes dynamically
for user_class, details in config.items():
    globals()[user_class] = create_user_class(user_class, details)

# We can set up a listener to stop the test when all data is processed
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Test has stopped.")
            
#TODO: Add more tasks as necessary for the load testing scenarios for each environment and use case
