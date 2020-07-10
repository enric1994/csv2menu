import requests

filename = '/examples/mim.csv'
headers = {
    'Content-Type': 'text/plain',
    'restaurant_name': 'GoDigital Restaurant',
    'output_id': 'mim'
}
url = "http://localhost:5000/menu"

with open(filename, 'rb') as f:
    response = requests.post(url, data=f, headers=headers)

print('Response Status Code: {}'.format(response.status_code))
