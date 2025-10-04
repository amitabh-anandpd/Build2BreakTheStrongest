import requests
import time

# Replace this with your target URL
url = "https://example.com/your-endpoint"

data = {
    "key": "value"
}

headers = {
    "Content-Type": "application/json"
}

for i in range(1, 10**9):
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"[{i}] Status: {response.status_code}, Response: {response.text}")
        time.sleep(1)  # delay between requests (in seconds)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)  # wait a bit before retrying
