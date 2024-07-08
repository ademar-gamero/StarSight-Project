import requests
import json
import sqlite3
import os
import geocoder
from math import asin, atan2, cos, degrees, radians, sin

class DB():
    def __init__(self, db_name):
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
            print("Your Saved Locations: ")
            print("----------------------")
            for row in rows:
                print(f'ID: {row[0]} || NAME: {row[1]} || LATITUDE: {row[3]} || LONGITUDE: {row[2]}')
                print("---------------------------------------------------------------------------------------------------------")

    def add_location(self, location):
        name = location[0]
        lat = location[1]
        lon = location[2]
        # checking if location is already saved
        query = '''SELECT COUNT(*) AS match_count FROM saved_locations 
              WHERE longitude = ? AND latitude = ? '''
        self.cur.execute(query, (lon, lat))
        result = self.cur.fetchone()[0]
        if result > 0:
            print("This location is already saved in the database")
        else:
            sql = '''INSERT INTO saved_locations(name,longitude,latitude)
                    VALUES(?,?,?)'''
            new_location = (name, lon, lat)
            self.cur.execute(sql, new_location)
            self.connection.commit()
            return self.cur.lastrowid
        return -1


class CityAPI():
    def __init__(self, latitude, longitude):
        self.location_latitude = latitude 
        self.location_longitude = longitude
        self.radius = 20

    def get_nearby_cities(self):
        response = requests.get(f"http://getnearbycities.geobytes.com/GetNearbyCities?radius={self.radius}&latitude={self.location_latitude}&longitude={self            .location_longitude}")
        city_list = json.loads(response.text) 
        return city_list

    def city_calculate(self, score_obj, city_list):
        if len(city_list) > 5:
            score_obj.lower_score(3)
            score_obj.light_pollution = 0
        else:
            if len(city_list[0]) > 0:
                for element in city_list:
                    name = element[1]
                    longitude = element[10]  
                    latitude = element[8]
                    api_url = f'https://api.api-ninjas.com/v1/city?name={name}'
                    response1 = requests.get(api_url, headers={'X-Api-Key':os.environ.get('NINJA_KEY')})
                    dict2 = json.loads(response1.text)
                    pop = dict2[0]["population"]
                    if 50000 <= pop <= 100000:
                        score_obj.lower_score(1)
                        score_obj.light_pollution -= 1
                        if score_obj.light_pollution < 0:
                            score_obj.light_pollution = 0
                    elif pop >= 100000:
                        score_obj.lower_score(3)
                        score_obj.light_pollution -= 3
                        if score_obj.light_pollution < 0:
                            score_obj.light_pollution = 0

class curr_user():
    def __init__(self):
        self.loc = geocoder.ip('me')    
        self.nearby_locs = [[]]

    def print_current_coords(self):
        print(self.loc.latlng)
    
    def current_lat(self):
        print(self.loc.latlng[0])
        return self.loc.latlng[0]

    def current_lon(self):
        print(self.loc.latlng[1])
        return self.loc.latlng[1]

    def get_nearby_locs(self):
        return self.nearby_locs

    #method that gets new locations based on bearing/dist
    def get_loc_given_dist_and_bear(self, lat1, lon1, dist, bearing, R=6371):
        #convert inputs to radians
        rad_lat1 = radians(lat1)
        rad_lon1 = radians(lon1)
        rad_bearing = radians(bearing)
        
        #calculate new points 
        rad_lat2 = asin(sin(rad_lat1)*cos(dist/R) + cos(rad_lat1) * sin(dist/R) * cos(rad_bearing))
        rad_lon2 = rad_lon1 + atan2(sin(rad_bearing) * sin(dist/R) * cos(rad_lat1),
                                cos(dist/R) - sin(rad_lat1) * sin(rad_lat2))

        #convert back to degrees from radians
        return (degrees(rad_lat2),degrees(rad_lon2))

    #recursive method that builds out the graph of nearby locations
    def calculate_nearby_locs(self,search_radius=20.0):
        pass

# score calculation/optimal for star gazing or not?            
class score:
    def __init__(self):
        self.score = 5
        self.light_pollution = 5
        self.score_card = {0:"NOT OPTIMAL-Stars will not be visible",
            1:"NOT OPTIMAL - Stars will not be visible",
            2:"NOT OPTIMAL - Stars will not be visible",
            3:"SUB OPTIMAL - Stars may be visible",
            4:"SUB OPTIMAL - Stars may be visible",
            5:"OPTIMAL - Stars will be visible"}
        self.light_pollution_card = {0:"HIGH LIGHT POLLUTION - large cities within 20 miles",
            1:"HIGH LIGHT POLLUTION - large cities within 20 miles",
            2:"HIGH LIGHT POLLUTION - large cities within 20 miles",
            3:"MEDIUM LIGHT POLLUTION - small or medium towns within 20 miles",
            4:"MEDIUM LIGHT POLLUTION - small or medium towns within 20 miles",
            5:"NO LIGHT POLLUTION - no cities within 20 miles"}
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
    def return_current_light_pollution_str(self):
        return self.light_pollution_card[self.light_pollution]

