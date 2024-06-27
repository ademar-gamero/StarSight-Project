import requests
import json
import sqlite3
import os
import sys

#add location
class DB():
    def __init__(self,db_name):
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
            print("Your Saved Locations")
            for row in rows:
                print(f'ID: {row[0]} NAME: {row[1]} LATITUDE: {row[2]} LONGITUDE: {row[3]}')

    def add_location(self,location):
        lat = location[1]
        lon = location[2]
        #checking if location is already saved
        query = '''SELECT COUNT(*) AS match_count FROM saved_locations 
              WHERE longitude = ? AND latitude = ? '''
        self.cur.execute(query,(lon,lat))
        result = self.cur.fetchone()[0]
        print(result)
        if result > 0:
            print("This location is already saved in the database")
        else:
            sql = '''INSERT INTO saved_locations(name,longitude,latitude)
                    VALUES(?,?,?)'''
            self.cur.execute(sql,location)
            self.connection.commit()
            return cur.lastrowid
        return -1
            

worst = False
city_counter = 0
location_longitude = None
location_latitude = None
a = 45.724115
b = -108.230242
radius = 20

class CityAPI():
    def __init__(self,latitude,longitude):
        self.location_latitude = latitude 
        self.location_longitude = longitude
        self.radius = 20
    def get_nearby_cities(self):
        response = requests.get(f"http://getnearbycities.geobytes.com/GetNearbyCities?radius={self.radius}&latitude={self.location_latitude}&longitude={self            .location_longitude}")
        city_list = json.loads(response.text) 
        return city_list
    def city_calculate(self,score_obj,city_list):
        if len(city_list) > 5:
            score_obj.lower_score(2)
        else:
            for element in city_list:
                name = element[1]
                longitude = element[10]  
                latitude = element[8]
                api_url = f'https://api.api-ninjas.com/v1/city?name={name}'
                response1 = requests.get(api_url,headers={'X-Api-Key':os.environ.get('NINJA_KEY')})
                dict2 = json.loads(response1.text)
                pop = dict2[0]["population"]
                if pop >= 50000:
                    score_obj.score(2)
    

#db connection
#connection = sqlite3.connect("star.db")
#cur = connection.cursor()
#cur.execute("SELECT * FROM saved_locations")
#rows = cur.fetchall()

#var = DB("star.db")
#var.print_rows()


#Asking for longitude and lattitude
'''
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
'''

#score calculation/optimal for star gazing or not?            
class score:
    def __init__(self):
        self.score = 5
        self.score_card = {0:"NOT OPTIMAL-Stars will not be visible",
            1:"NOT OPTIMAL-Stars will not be visible",
            2:"NOT OPTIMAL-Stars will not be visible",
            3:"SUB OPTIMAL-Stars may be visible",
            4:"SUB OPTIMAL-Stars may be visible",
            5:"OPTIMAL-Stars will be visible"}
    def lower_score(self,val):
        self.score = self.score - val
        if self.score < 0:
            self.score = 0
    def return_current_score(self):
        return self.score
    def print_current_score(self):
        print(self.score)
    def return_current_score_str(self):
        return self.score_card[self.score]

        
#resp = input("Would you like to save the location(y)(n)?")
#if resp == "y":
    #name_given = input("What would you like to name this location?")
    #location = (name_given,location_longitude,location_latitudes)
    #add_location(connection,location)
#elif resp == "n":
    #resp1 = input("would you like to try looking up another location(y)(n)?")

