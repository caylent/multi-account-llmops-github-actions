# API Load Testing Guide

This guide provides instructions on how to perform load testing on various API endpoints using Locust, an open-source load testing tool. The testing script supports multiple environments and use cases for our APIs.

## Prerequisites

Before running the tests, ensure you have the following prerequisites:

- Python 3.x installed
- Locust installed (`pip install locust`)
- An API key for authenticating requests

## Setting Up the Environment

1. **API Key**: Ensure the API key is stored securely. It's recommended to use an environment variable to store the API key. You can set it in the shell like this:

    ```bash
    export API_KEY='your_actual_api_key_here'
    ```

2. **Install Dependencies**: If not already installed, you can install Locust using pip:
    
    ```bash
    pip install locust
    ```

## Configuration

Edit the `api_config.json` file to update the API endpoints, paths, and request data for different user classes. You can also update the config file for future use cases.

## Running the Tests

Run Locust using the command below, specifying the user class to simulate based on the configurations defined in `api_config.json`:

- **Without Web UI (headless mode)**:
    
    ```bash
    locust -f api_load_tests/api_load_test.py --headless -u <number_of_users> -r <spawn_rate> --run-time <time> --html <report_name>.html --csv <csv_name> <UserClassName>
    ```

    Where:
    - `<number_of_users>` is the number of concurrent users.
    - `<spawn_rate>` is the rate per second in which users will spawn.
    - `<time>` is the duration for which the test will run (e.g., 1m for one minute).
    - `<report_name>.html` is the name of the file to save the HTML report.
    - `<csv_name>` is the prefix for the CSV files that will store the test results.
    - `<UserClassName>` is the name of the user class to simulate

    **Example**:
    ```bash
    locust -f api_load_tests/api_load_test.py --headless -u 60 -r 1 --run-time 2m --html report.html --csv report BetaEmailTypeUser
    ```

- **With Web UI**:

    Start Locust without the headless flag to open the web interface:

    ```bash
    locust -f api_load_tests/api_load_test.py
    ```

    This will start a web server on `http://localhost:8089` where you can configure the number of users, spawn rate, and view real-time statistics.

## Analyzing the Results

After the test runs, review the HTML report and CSV files for detailed metrics about response times, request rates, and failure rates. This will help in assessing the performance and stability of the API endpoints.

## Additional Notes

- Modify the JSON configuration file as necessary to adapt to new testing scenarios.
- Ensure the API key and endpoint configurations are up to date before running tests.
- Use the environment variable `API_KEY` to securely pass the API credentials during tests.
