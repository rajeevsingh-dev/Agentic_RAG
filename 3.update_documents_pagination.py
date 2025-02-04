import requests
import json
import time

# Azure Search service details
service_name = '<servicename>.search.windows.net'
api_version = '2023-10-01-Preview'  # Updated API version
api_key = '<your-search-api-key>'
index_name = '<index-name>'


batch_size = 10

def get_all_documents():
    all_documents = []
    skip = 0
    top = 8

    while True:
        url = f"https://{service_name}/indexes/{index_name}/docs"
        params = {
            'api-version': api_version,
            'search': '*',
            '$skip': skip,
            '$top': top,
            '$count': 'true',
            '$select': 'chunk_id,chunk_id_new'
        }
        headers = {
            'Content-Type': 'application/json',
            'api-key': api_key
        }

        try:
            print(f"Fetching documents {skip} to {skip + top}...")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            documents = data.get('value', [])
            if not documents:
                break
                
            all_documents.extend(documents)
            total_count = data.get('@odata.count', 0)
            print(f"Retrieved {len(all_documents)}/{total_count} documents")
            
            if len(all_documents) >= total_count:
                break
                
            skip += top
            time.sleep(0.5)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving documents: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            break

    return all_documents

def update_documents(batch):
    url = f"https://{service_name}/indexes/{index_name}/docs/index?api-version={api_version}"
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key
    }
    
    data = {
        "value": [
            {
                "@search.action": "mergeOrUpload",
                "chunk_id": doc['chunk_id'],
                "chunk_id_new": str(doc.get('chunk_id', '')) if doc.get('chunk_id') else None
            } for doc in batch
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error updating batch: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")
        return False

def main():
    print("Starting document retrieval...")
    all_documents = get_all_documents()
    
    if all_documents:
        print(f"\nUpdating {len(all_documents)} documents in batches of {batch_size}...")
        for i in range(0, len(all_documents), batch_size):
            batch = all_documents[i:i + batch_size]
            if update_documents(batch):
                print(f"Updated batch {i//batch_size + 1}")
            time.sleep(1)  # Prevent throttling
    else:
        print("No documents retrieved")

if __name__ == "__main__":
    main()