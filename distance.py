import requests
import json



counter = 5

longitude = -108.230242
latitude = 45.724115
location = longitude,latitude
radius = 20
response = requests.get(f"http://getnearbycities.geobytes.com/GetNearbyCities?radius={radius}&latitude={latitude}&longitude={longitude}")
dict = json.loads(response.text) 
print(dict)

if len(dict) > 5:
    counter -= 2

for key in dict:
    response = requests.get("city")
    dict2 = json.loads(response.text)
    if dict2["population"] < 50,000:
        continue
    else:
        counter -= 1
