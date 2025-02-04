#Running Code
#this code creates a new Field in the existing Index

import requests
import json


# Azure Search service details
service_name = '<servicename>.search.windows.net'
api_version = '2023-10-01-Preview'  # Updated API version
api_key = '<your-search-api-key>'
index_name = '<index-name>'


# Step 1: Retrieve the existing index schema
url = f"https://{service_name}/indexes/{index_name}?api-version={api_version}"
headers = {
    'Content-Type': 'application/json',
    'api-key': api_key
}
response = requests.get(url, headers=headers)
index_schema = response.json()

# Step 2: Modify the schema to add the new field
new_field = {
    "name": "chunk_id_new",
    "type": "Edm.String",
    "filterable": True,
    "retrievable": True
}
index_schema['fields'].append(new_field)

# Step 3: Update the index with the modified schema
url = f"https://{service_name}/indexes/{index_name}?api-version={api_version}"
response = requests.put(url, headers=headers, data=json.dumps(index_schema))

if response.status_code in [200, 204]:
    print("Index updated successfully.")
else:
    print(f"Error updating index: {response.status_code} - {response.text}")