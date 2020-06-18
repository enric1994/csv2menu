import requests

filename = 'examples/menu_2.csv'
headers = {'Content-Type': 'text/plain'}
url = "http://localhost:5000/menu"

with open(filename, 'rb') as f:
    request = requests.post(url, data=f, headers=headers)

print(request)
