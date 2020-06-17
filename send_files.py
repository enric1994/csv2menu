import requests

headers = {'Content-Type': 'text/plain'}
url = "http://localhost:5000/menu"

with open('menu.csv', 'rb') as file:
    req = requests.post(url, data=file, headers=headers)

print(req)
