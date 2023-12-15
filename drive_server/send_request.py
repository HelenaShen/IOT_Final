import requests
import json
import os
import sys

def send_request(datetime_str):
    url = "http://127.0.0.1:5000/upload"
    headers = {'Content-Type': 'application/json'}
    data = {"datetime": datetime_str}

    json_data = json.dumps(data)
    response = requests.post(url, headers=headers, data=json_data)
    print(response.json())

if __name__ == "__main__":
    datetime_str = sys.argv[1]
    send_request(datetime_str)

