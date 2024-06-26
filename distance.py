import requests
import json
import sqlite3
import os

#add location
def add_location(connection,location):
    sql = '''INSERT INTO saved_locations(name,longitude,latitude)
            VALUES(?,?,?)'''
    cur = connection.cursor()
    cur.execute(sql,location)
    connection.commit()
    return cur.lastrowid

counter = 5
worst = False
location_longitude = -108.230242
location_latitude = 45.724115
radius = 20
#response = requests.get(f"http://getnearbycities.geobytes.com/GetNearbyCities?radius={radius}&latitude={latitudes}&longitude={longitudes}")
#dict = json.loads(response.text) 

#db connection
connection = sqlite3.connect("star.db")
cur = connection.cursor()
cur.execute("SELECT * FROM saved_locations")
rows = cur.fetchall()
#intro prompt
print("Hello!, Welcome to the star gazer app!")
print("Your saved locations: ")
for row in rows:
    print(row)
#Asking for longitude and lattitude
response = int(input("Enter 0 to lookup a new location or enter a number matching a location to look up a saved location: "))    
if response == 0:
    location_latitude = float(input("Enter a latitude: "))
    location_longitude = float(input("Enter a longitude: "))
    
else:
    entry = response - 1
    if 0 > entry >= len(rows):
        print("entry not found")
    else:
        location_latitude = rows[entry][2]
        location_longitude = rows[entry][3]
print(location_latitude)
print(location_longitude)

#if len(dict) > 5:
    #counter -= 2
#else:
    #for element in dict:
        #name = element[1]
        #longitude = element[10]  
        #latitude = element[8]
        #api_url = f'https://api.api-ninjas.com/v1/city?name={name}'
        #response1 = requests.get(api_url,headers={'X-Api-Key':os.environ.get('NINJA_KEY')})
        #dict2 = json.loads(response1.text)
        #pop = dict2[0]["population"]
        #if pop >= 50000:
            #counter -= 2
        #if counter == 0:
            #worst = True
            #break

#score calculation/optimal for star gazing or not?            
score_card = ("Location not optimal for stargazing")

resp = input("Would you like to save the location(y)(n)?")
if resp == "y":
    name_given = input("What would you like to name this location?")
    location = (name_given,location_longitude,location_latitudes)
    add_location(connection,location)
else:
    print("Thanks for using the application")
