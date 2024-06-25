import requests
import json


counter = 5
longitude = -108.230242
latitude = 45.724115
location = longitude,latitude
radius = 20
response = requests.get(f"http://getnearbycities.geobytes.com/GetNearbyCities?radius={radius}&latitude={latitude}&longitude={longitude}")
dict = json.loads(response.text) 

if len(dict) > 5:
    counter -= 2
else:
    for element in dict:
        name = element[1]
        longitude = element[10]  
        latitude = element[8]
        api_url = f'https://api.api-ninjas.com/v1/city?name={name}'
        response1 = requests.get(api_url,headers={'X-Api-Key':"ex8H0bQ796On3t6f4lrWbw==DqHZjWAAgliP1fGH"})
        dict2 = json.loads(response1.text)
        pop = dict2[0]["population"]
        if pop >= 50,000:
            counter -= 2
