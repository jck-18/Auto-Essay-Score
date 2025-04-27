import requests
import json

# URL of the API
url = "http://127.0.0.1:5000/"

# Sample essay (more than 20 characters)
sample_essay = """
This is a test essay to check if our Automatic Essay Scoring system is working.
The essay should be long enough to provide meaningful scoring and demonstrate
that the API is functioning properly. This text is just for testing purposes.
"""

# Prepare the request data
data = {"text": sample_essay}

try:
    # Send POST request to the API
    print("Sending request to", url)
    print("Request data:", data)
    response = requests.post(url, json=data)
    
    # Print the result
    print("Status Code:", response.status_code)
    if response.status_code == 200 or response.status_code == 201:
        print("Response:", response.json())
    else:
        print("Error response:", response.text)
except Exception as e:
    print("Error occurred:", str(e)) 