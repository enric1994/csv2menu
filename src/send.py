import requests

filename = '/examples/menu.csv'
headers = {
    'Content-Type': 'text/plain',
    'restaurant_name': 'Restaurant_Name_',
    'output_id': '123'
}
url = "http://localhost:5000/menu"

with open(filename, 'rb') as f:
    response = requests.post(url, data=f, headers=headers)

print('Response Status Code: {}'.format(response.status_code))
