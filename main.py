from distance import DB,CityAPI,score 
from weather-api import WeatherAPI

#db intialization
var = DB("star.db")
print("Hello!, Welcome to the star sight app!")
#Description
print("This application lets you see the condition for viewing stars and visible constellations given a location(lattitude/longitude)")
print("You can also save locations you lookup to come back to them in the future")
#Menu
print("Lookup new location(n)")
print("Look at saved/select locations(o)")
print("Quit(q)")
#Look up New location
resp = input("Enter your response: ")
if resp == "n":
    print("Enter a valid latitude and longitude value")
        while not isinstance(location_latitude,float) or not isinstance(location_longitude,float):
            location_latitude = input("Enter a latitude: ")
            if location_latitude == "q":
                print("cya l8ter alligator")
                sys.exit()
            location_longitude = input("Enter a longitude: ")
            if location_longitude == "q":
                print("cya l8ter alligator")
                sys.exit()
            if not isinstance(location_latitude,float):
                print("please enter a valid latitude decimal value")
            if not isinstance(location_longitude,float):
                print("please enter a valid longitude decimal value")
elif resp == "o":
    print = ("Your saved locations: ")
    var.print_rows()
    resp_saved = input("If you would like to select a saved location to view again enter the associated id with it otherwise enter 0 to return: ")
    if resp_saved == 0
        continue
    else:
        while(not isinstance(resp,))
        entry = response - 1
        if 0 > entry >= len(rows):
            print("entry not found")
        else:
            location_latitude = rows[entry][2]
            location_longitude = rows[entry][3] 
elif resp == "q":
    #Quit
else:
    print("You did not enter a valid option(n)(o)(q)!")
    print("please try again")


#Asking for longitude and lattitude , check if location is valid as well
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


#pseudo code
#while loop
# nested while loops to make sure input is accurate
# if the location is not valid, can be float value but invalid location


