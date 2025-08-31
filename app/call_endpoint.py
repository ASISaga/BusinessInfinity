import requests

# Replace with your endpoint URL and key
ep_url = "https://<your-endpoint-name>.<region>.inference.ml.azure.com/score"
api_key = "<your-endpoint-key>"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}


# Example payload with adapter selection
data = {
    "adapter_name": "qv",  # or "ko" or any available adapter
    "input_data": "your input here"
}

response = requests.post(ep_url, headers=headers, json=data)
print("Status code:", response.status_code)
print("Response:", response.json())
