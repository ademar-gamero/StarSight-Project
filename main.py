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
resp = None
while(resp != "q"):
    print("Hello!, Welcome to the star sight app!")
    #Description
    print("This application lets you see the condition for viewing stars and visible constellations given a location(lattitude/longitude)")
    print("You can also save locations you lookup to come back to them in the future")
    print("Calculations based on these assumptions: Time 22:00-3:00 | Current Date")
    #Menu
    print("Lookup a new location(n)")
    #I think we should add this 
    #print("Lookup nearby locations for star gazing(c)")
    print("Look at saved/select locations(o)")
    print("Quit(q)")
    #Look up New location
    resp = input("Enter your response: ")
    if resp == "n":
        flag1 = False
        while flag1 == False:
            print("Enter a valid latitude and longitude value: ") #need to add range check in united states for long and latitude 
            try:
                location_latitude = float(input("Enter a latitude: "))
            except ValueError:
                print("Please enter a valid latitude")
                continue
            try:
                location_longitude = float(input("Enter a longitude: "))
            except ValueError:
                print("Please enter a valid longitude")
                continue
            flag1 = True
        
        city = CityAPI(location_latitude,location_longitude)
        local = city.get_nearby_cities()

        ## score calculation/report
        city.city_calculate(score_obj,local)
        weather_deduction = WeatherAPI.get_weather(location_latitude,location_longitude)
        score_obj.lower_score(weather_deduction)
        print(f'Conditions for StarGazing: {score_obj.return_current_score_str()}')



        save_or_no = None
        while save_or_no != "y" and save_or_no != "n":
            save_or_no = input("Would you like to save this location(y)(n)?")
            if save_or_no == "y":
                name = input("Enter a name for your location: ")
                location = (name,location_latitude,location_longitude)
                db.add_location(location)
            elif save_or_no != "n":
                print("please enter either (y) or (n)")
        #continue? or stop    
        cont_or_stop = None
        while cont_or_stop != "y" and cont_or_stop != "n":
            cont_or_stop = input("Would you like to continue using the application(y)(n)?")
            if cont_or_stop == "y":
                print("*************************************************************")
                print("*************************************************************")
                continue
            elif cont_or_stop == "n":
                print("Thank you for using the StarSight application")
                resp = "q"
            else:
                print("Please enter either (y) or (n)")
            

    elif resp == "o":
        print = ("Your saved locations: ")
        db.print_rows()
        rows = db.saved_locations()
        flag2 = False
        while flag2 == False: 
            try:
                resp_saved = int(input("If you would like to select a saved location to view again enter the associated id with it otherwise enter 0 to return: "))#catch exception
            except ValueError:
                print("Please enter a valid id ")
                continue
            flag2 = True
        if resp_saved == 0:
            pass #change to continue once full loop is implemented
        else:
            entry = resp_saved - 1
            if entry < 0 or entry >= len(rows):
                print("entry not found or not in bounds")
            else:
                location_latitude = rows[entry][2]
                location_longitude = rows[entry][3] 
                flag = True
                
        city = CityAPI(location_latitude,location_longitude)
        local = city.get_nearby_cities()

        ## score calculation/report
        city.city_calculate(score_obj,local)
        weather_deduction = WeatherAPI.get_weather(location_latitude,location_longitude)
        score_obj.lower_score(weather_deduction)
        print(f'Conditions for StarGazing: {score_obj.return_current_score_str()}')
        #gather data on location
        #score report 
    elif resp == "q":
        print("Thank You for using the StarSight Application. Live Long and Prosper...")
        sys.exit()
    else:
        print("You did not enter a valid option(n)(o)(q)!")
        print("please try again")
        print("*************************************************************")
        print("*************************************************************")



#pseudo code
#while loop
# nested while loops to make sure input is accurate
# if the location is not valid, can be float value but invalid location


