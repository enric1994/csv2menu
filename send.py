import requests

headers = {
    'Content-Type': 'text/plain',
    'restaurantname': 'Example Restaurant',
    'restaurantid': '12345',
    'customeremail': 'email@example.com',
    'locale': 'en'
}
url = "https://api.godigital.menu/tracking"

response = requests.post(url, headers=headers)

print(response.text)
