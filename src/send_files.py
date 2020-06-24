import requests

filename = '/examples/menu_3.csv'
headers = {
    'Content-Type': 'text/plain',
    'restaurant_name': 'Example Restaurant',
    'output_id': '123'
}
url = "http://localhost:5000/menu"

with open(filename, 'rb') as f:
    request = requests.post(url, data=f, headers=headers)

print(request)