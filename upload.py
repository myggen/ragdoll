#!/usr/bin/env python3

import requests

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImFlYjZkY2MzLTU0MmEtNGEyNS1hMzY3LWJiMWMwYWEzZjE0OCJ9.b5DW1HvLL_GAmrhwKiGCCy1TGsNC4BwhnnOMEEYh32k'
def upload_file(token, file_path):
    url = 'http://localhost:3000/api/v1/files/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response.json()

def add_file_to_knowledge(token, knowledge_id, file_id):
    url = f'http://localhost:3000/api/v1/knowledge/{knowledge_id}/file/add'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


#resp = upload_file(token, '/home/espenm/space/projects/data/retningslinjer-met/Retningslinjeforreiserv2.1.html')
#print(resp)

resp = add_file_to_knowledge(token, 'bbf43746-1946-46f4-8f80-5a7ad9925219', '21c5302e-a7fb-4310-b97d-96694fb27c8a')
print(resp)