import requests
import json
import sqlite3
import os

counter = 5
worst = False
longitudes = -108.230242
latitudes = 45.724115
location = longitude,latitude
radius = 20
response = requests.get(f"http://getnearbycities.geobytes.com/GetNearbyCities?radius={radius}&latitude={latitudes}&longitude={longitudes}")
dict = json.loads(response.text) 
connection = sqlite3.connect("star.db")
if len(dict) > 5:
    counter -= 2
else:
    for element in dict:
        name = element[1]
        longitude = element[10]  
        latitude = element[8]
        api_url = f'https://api.api-ninjas.com/v1/city?name={name}'
        response1 = requests.get(api_url,headers={'X-Api-Key':os.environ.get('NINJA_KEY')})
        dict2 = json.loads(response1.text)
        pop = dict2[0]["population"]
        if pop >= 50000:
            counter -= 2
        if counter == 0:
            worst = True
            break
resp = print(input("Would you like to save the location(y)(n)?"))
if resp == "y":
    name_given = print(input("What would you like to name this location?"))
else:
    print("Thanks for using the application")
