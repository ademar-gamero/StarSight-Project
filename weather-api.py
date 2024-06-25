import requests
import json
import os

my_api_key = os.getenv('API_KEY')

url="http://api.weatherapi.com/v1/current.json"


response = requests.post(url, {
    'key': my_api_key,
    'q': '11434',
})

print(response.json())
