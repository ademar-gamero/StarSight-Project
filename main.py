from distance import DB,CityAPI,score 
from weather_api import WeatherAPI
import sys

#db intialization
db = DB("star.db")
#score intialization
score_obj = score()
#location intialization
location_latitude = None
location_longitude = None
print("Hello!, Welcome to the star sight app!")
#Description
print("This application lets you see the condition for viewing stars and visible constellations given a location(lattitude/longitude)")
print("You can also save locations you lookup to come back to them in the future")
#Menu
print("Lookup a new location(n)")
#I think we should add this 
#print("Lookup nearby locations for star gazing(c)")
print("Look at saved/select locations(o)")
print("Quit(q)")
#Look up New location
resp = input("Enter your response: ")
if resp == "n":
    print("Enter a valid latitude and longitude value")
    while not isinstance(location_latitude,float) or not isinstance(location_longitude,float):
        location_latitude = float(input("Enter a latitude: "))
        if location_latitude == "q":
            print("cya l8ter alligator")
            sys.exit()
        location_longitude = float(input("Enter a longitude: "))
        if location_longitude == "q":
            print("cya l8ter alligator")
            sys.exit()
        if not isinstance(location_latitude,float):
            print("please enter a valid latitude decimal value")
        if not isinstance(location_longitude,float):
            print("please enter a valid longitude decimal value")
    city = CityAPI(location_latitude,location_longitude)
    local = city.get_nearby_cities()
    city.city_calculate(score_obj,local)
    save_or_no = input("Would you like to save this location(y)(n)?")
        if save_or_no = "y":
            name = input("Enter a name for your location: ")
            location = (name,location_latitude,location_longitude)
            db.add_location(location)
        else:
            #continue back to start menu once loop is implemented
    # save location?
    # enter name for location?
        

elif resp == "o":
    print = ("Your saved locations: ")
    db.print_rows()
    rows = db.saved_locations()
    resp_saved = int(input("If you would like to select a saved location to view again enter the associated id with it otherwise enter 0 to return: "))#catch exception
    if resp_saved == 0:
        pass #change to continue once full loop is implemented
    else:
        flag = False 
        while flag == False:
            if isinstance(resp_saved,int):
                print("Please enter a valid integer value")
            else:
                entry = resp_saved - 1
            if entry < 0 or entry >= len(rows):
                print("entry not found or not in bounds")
            else:
                location_latitude = rows[entry][2]
                location_longitude = rows[entry][3] 
                flag = True
elif resp == "q":
    Print("Thank You for using the StarSight Application. Live Long and Prosper")
    sys.exit()
else:
    print("You did not enter a valid option(n)(o)(q)!")
    print("please try again")



#pseudo code
#while loop
# nested while loops to make sure input is accurate
# if the location is not valid, can be float value but invalid location


