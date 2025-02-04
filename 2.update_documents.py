import requests
import json

# Azure Search service details
service_name = '<servicename>.search.windows.net'
api_version = '2023-10-01-Preview'  # Updated API version
api_key = '<your-search-api-key>'
index_name = '<index-name>'


# Step 1: Retrieve existing documents
url = f"https://{service_name}/indexes/{index_name}/docs?api-version={api_version}&search=*"
headers = {
    'Content-Type': 'application/json',
    'api-key': api_key
}


response = requests.get(url, headers=headers)
documents = response.json()['value']

#print("response:", response)
#print("documents:", documents)



# Step 2: Update documents with the new field
for doc in documents:
    doc['chunk_id_new'] = str(doc['chunk_id'])  # Example: Assign chunk_id based on existing id


# Step 3: Upload updated documents
url = f"https://{service_name}/indexes/{index_name}/docs/index?api-version={api_version}"
headers = {
    'Content-Type': 'application/json',
    'api-key': api_key
}
data = {
    "value": [{"@search.action": "mergeOrUpload", **doc} for doc in documents]
}


response = requests.post(url, headers=headers, data=json.dumps(data))



#if response.status_code == 200:
#    print("Documents updated successfully.")
#else:
#    print(f"Error updating documents: {response.status_code} - {response.text}")



def verify_updates():
    try:
        # Verify URL construction
        verify_url = f"https://{service_name}/indexes/{index_name}/docs?api-version={api_version}&search=*"
        verify_headers = {
            'Content-Type': 'application/json',
            'api-key': api_key
        }

        # Get updated documents with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(verify_url, headers=verify_headers)
                response.raise_for_status()
                updated_documents = response.json()['value']
                
                print("\nVerification Results:")
                print(f"Total documents found: {len(updated_documents)}")
                
                # Count documents with/without new field
                docs_with_new_field = sum(1 for doc in updated_documents if doc.get('chunk_id_new') is not None)
                docs_without_new_field = len(updated_documents) - docs_with_new_field
                
                print(f"Documents with chunk_id_new: {docs_with_new_field}")
                print(f"Documents without chunk_id_new: {docs_without_new_field}")
                
                # Print detailed status for documents missing the new field
                if docs_without_new_field > 0:
                    print("\nDocuments missing chunk_id_new:")
                    for doc in updated_documents:
                        if doc.get('chunk_id_new') is None:
                            print(f"ID: {doc.get('id', 'unknown')}, chunk_id: {doc.get('chunk_id', 'none')}")
                
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
    except requests.exceptions.RequestException as e:
        print(f"Error verifying updates: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

# Call verification after successful update
if response.status_code == 200:
    print("Documents updated successfully.")
    verify_updates()
else:
    print(f"Error updating documents: {response.status_code} - {response.text}")