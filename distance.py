import requests
import json
import sqlite3
import os
import sys

#add location
class DB():
    def __init__(self,db_name):
        if db_name != "star.db":
            print("Invalid Database")
            sys.exit()
        self.connection = sqlite3.connect(db_name)
        self.cur = self.connection.cursor()
        
    def saved_locations(self):
        self.cur.execute("SELECT * FROM saved_locations")
        rows = self.cur.fetchall()
        if rows == None:
            return 0
        else:
            return rows
    
    def print_rows(self):
        rows = self.saved_locations()
        if rows == 0:
            print("No locations have been saved")
        else:
            for row in rows:
                print(row)

    def add_location(self,location):
        sql = '''INSERT INTO saved_locations(name,longitude,latitude)
                VALUES(?,?,?)'''
        self.cur.execute(sql,location)
        self.connection.commit()
        return cur.lastrowid

class Prompt():
    def __init__(self,latitude,longitude):
        self.location

counter = 5
worst = False
city_counter = 0
location_longitude = None
location_latitude = None
a = 45.724115
b = -108.230242
radius = 20

#response = requests.get(f"http://getnearbycities.geobytes.com/GetNearbyCities?radius={radius}&latitude={latitudes}&longitude={longitudes}")
#dict = json.loads(response.text) 

#db connection
#connection = sqlite3.connect("star.db")
#cur = connection.cursor()
#cur.execute("SELECT * FROM saved_locations")
#rows = cur.fetchall()

var = DB("star.db")
var.print_rows()

#intro prompt
print("Hello!, Welcome to the star gazer app!")
print("if you would like to quit enter \q at anytime a prompt is given")
print("Your saved locations: ")

#Asking for longitude and lattitude
response = int(input("Enter 0 to lookup a new location or enter a number matching a location to look up a saved location: "))    
if response == 0:
    while not isinstance(location_latitude,float) or not isinstance(location_longitude,float):
        location_latitude = input("Enter a latitude: ")
        if location_latitude == "\q":
            print("cya l8ter alligator")
            sys.exit()
        location_longitude = input("Enter a longitude: ")
        if location_longitude == "\q":
            print("cya l8ter alligator")
            sys.exit()
        if not isinstance(location_latitude,float):
            print("please enter a valid latitude decimal value")
        if not isinstance(location_longitude,float):
            print("please enter a valid longitude decimal value")
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
    #city_counter += 6
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
class score():
    def __init__:
        self.score = 5
        self.score_card = {0:"NOT OPTIMAL-Stars will not be visible",
            1:"NOT OPTIMAL-Stars will not be visible",
            2:"NOT OPTIMAL-Stars will not be visible",
            3:"SUB OPTIMAL-Stars may be visible",
            4:"SUB OPTIMAL-Stars may be visible",
            5:"OPTIMAL-Stars will be visible"}
    def return_current_score():
        return self.score
    def print_current_score():
        print(self.score)
    def return_current_score_str():
        return self.score_card[self.score]

        
resp = input("Would you like to save the location(y)(n)?")
if resp == "y":
    name_given = input("What would you like to name this location?")
    location = (name_given,location_longitude,location_latitudes)
    add_location(connection,location)
elif resp == "n":
    resp1 = input("would you like to try looking up another location(y)(n)?")

