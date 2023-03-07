import requests

import time



resp = requests.post('http://127.0.0.1:5000/upscale', files={
    'image_1': open('lama_300px.png', 'rb')
})
resp_data = resp.json()
print(resp_data)
task_id = resp_data.get('task_id')
print(task_id)
#

while True:
    resp = requests.get(f'http://127.0.0.1:5000/tasks/{task_id}')
    print(resp.json())
    time.sleep(10)
    if resp.json()['status'] == 'SUCCESS':
        print('ok')
        break
