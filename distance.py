import requests
import json
import sqlite3
import os
import geocoder
import haversine as hs
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
                    if dict2 == []:
                        return
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
        self.user_nearby_locs = []
        self.coords = self.loc.latlng
        self.guide = {8.04672:1.60934*4,16.0934:3.21869*4,32.1869:6.43738*4}

    def print_current_coords(self):
        print(self.loc.latlng)
    
    def current_lat(self):
        print(self.loc.latlng[0])
        return self.loc.latlng[0]

    def current_lon(self):
        print(self.loc.latlng[1])
        return self.loc.latlng[1]

    def print_user_nearby_locs(self):
        print(self.user_nearby_locs)

    #method that gets new locations based on bearing/dist
    def get_loc_given_dist_and_bear(self, lat1, lon1, dist, bearing, R=6371):
        #convert inputs to radians
        lat1 = float(lat1)
        lon1 = float(lon1)
        rad_lat1 = radians(lat1)
        rad_lon1 = radians(lon1)
        rad_bearing = radians(bearing)
        
        #calculate new points 
        rad_lat2 = asin(sin(rad_lat1)*cos(dist/R) + cos(rad_lat1) * sin(dist/R) * cos(rad_bearing))
        rad_lon2 = rad_lon1 + atan2(sin(rad_bearing) * sin(dist/R) * cos(rad_lat1),
                                cos(dist/R) - sin(rad_lat1) * sin(rad_lat2))

        #convert back to degrees from radians
        lat2 = degrees(rad_lat2)
        lon2 = degrees(rad_lon2)
        coords = (lat2,lon2)
        return coords

    #recursive method that builds out the graph of nearby locations
    '''
    def calculate_nearby_locs(self,nearby_locs,origin_loc, prev_loc, current_loc,search_radius=32.1869):
        if hs.haversine(origin_loc,current_loc) > search_radius:
            return None
        else:
            nearby_locs.append(current_loc)
        prev_loc = current_loc
        self.calculate_nearby_locs(nearby_locs,origin_loc,prev_loc,self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],1.60934,0),search_radius)#north
        self.calculate_nearby_locs(nearby_locs,origin_loc,prev_loc,self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],1.60934,90),search_radius)#east
        self.calculate_nearby_locs(nearby_locs,origin_loc,prev_loc,self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],1.60934,180),search_radius)#south
        self.calculate_nearby_locs(nearby_locs,origin_loc,prev_loc,self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],1.60934,270),search_radius)#west
        return None
    '''
    '''
    def calculate_nearby_locs(self,nearby_locs,origin_loc,search_radius=8.04672):
        queue = []

        queue.append(origin_loc)
        
        while len(queue) > 0:
            prev_loc = queue.pop(0)

            north = self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],6.43738,0)#north
            if hs.haversine(origin_loc,north) <= search_radius and north not in queue and north not in nearby_locs:
                print(hs.haversine(origin_loc,north))
                queue.append(north)
                nearby_locs.append(north) 
            east = self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],6.43738,90)#east
            if hs.haversine(origin_loc,east) <= search_radius and east not in queue and east not in nearby_locs:
                queue.append(east)
                nearby_locs.append(east) 
            south = self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],6.43738,180)#south
            if hs.haversine(origin_loc,south) <= search_radius and south not in queue and south not in nearby_locs:
                queue.append(south)
                nearby_locs.append(south) 
            west = self.get_loc_given_dist_and_bear(prev_loc[0],prev_loc[1],6.43738,270)#west
            if hs.haversine(origin_loc,west) <= search_radius and west not in queue and west not in nearby_locs:
                queue.append(west)
                nearby_locs.append(west) 
    '''      
    def calculate_nearby_locs(self,nearby_locs,origin_loc,search_radius=8.04672):
        lat = float(origin_loc[0])
        lon = float(origin_loc[1])
        origin_loc = (lat,lon)
        dist_bw_points = self.guide[search_radius] 

        vertex = int(search_radius/ dist_bw_points) 

        print(vertex)
        count = 0
        for x in range(-vertex,vertex + 1):
            new_lat = self.get_loc_given_dist_and_bear(origin_loc[0], origin_loc[1], abs(x) * dist_bw_points, 0 if x >= 0 else 180)
            if hs.haversine(origin_loc,new_lat) <= search_radius and new_lat not in nearby_locs :
                count += 1
                nearby_locs.append({'lat':new_lat[0], 'lng':new_lat[1], 'label':f'Marker {count}'})

        for y in range(-vertex,vertex + 1):
            new_lon = self.get_loc_given_dist_and_bear(origin_loc[0], origin_loc[1], abs(y) * dist_bw_points, 90 if y >= 0 else 270)
            if hs.haversine(origin_loc,new_lon) <= search_radius and new_lon not in nearby_locs:
                count += 1
                nearby_locs.append({'lat':new_lon[0], 'lng':new_lon[1], 'label':f'Marker {count}'})
        #if search_radius == 8.04672:
            #nearby_locs.pop(5)
        #else:
            #nearby_locs.pop(4)
        return nearby_locs

# score calculation/optimal for star gazing or not?            
class score():
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

