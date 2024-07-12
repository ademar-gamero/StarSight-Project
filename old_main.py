from distance import DB,CityAPI,score1,curr_user 
from weather_api import WeatherAPI
import sys

# db intialization
db = DB("star.db")
# score intialization

# location intialization
location_latitude = None
location_longitude = None
resp = None
while resp != "q":
    cur_usr = curr_user()
    score_obj = score1()
    location_latitude = None
    location_longitude = None
    print("***************************************")
    print("Hello!, Welcome to the star sight app!")
    # Description
    print("This application lets you see the condition for viewing stars and lunar phases of a given location(lattitude/longitude)")
    print("You can also save locations you lookup to come back to them in the future")
    print("***************************************************************************************")
    print("IMPORTANT: Calculations are based on these assumptions: Time 22:00-3:00 | Current Date")
    print("***************************************************************************************")
    # Menu
    print("                                        Menu")
    print("***************************************************************************************")
    print("                             Lookup a new location(n)")
    # I think we should add this 
    # print("Lookup nearby locations for star gazing(c)")
    print("                         Look at saved/select locations(o)")
    print("                                       Quit(q)")
    print("Your Current Location: ")
    cur_usr.print_current_coords()
    cur_usr.current_lat()
    cur_usr.current_lon()
    cur_usr.get_loc_given_dist_and_bear(43.1777903, -88.0052169, 4.82803, 270)

    cur_usr.calculate_nearby_locs(cur_usr.user_nearby_locs,cur_usr.coords)
    print(cur_usr.user_nearby_locs)
    print(len(cur_usr.user_nearby_locs))
    

    # Look up New location
    resp = input("Enter your response: ")
    if resp == "n":
        flag1 = False
        while flag1 == False:
            print("Enter a valid latitude and longitude value: ")  #need to add range check in united states for long and latitude 
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
        print("-----------------------------------------")
        city = CityAPI(location_latitude,location_longitude)
        local = city.get_nearby_cities()

        city.city_calculate(score_obj,local)  ## score calculation/report
        weather_response = WeatherAPI.get_weather_response(location_latitude,location_longitude)
        weather_deduction = WeatherAPI.get_weather_score(weather_response)
        
        score_obj.lower_score(weather_deduction)
        print(f'Conditions for StarGazing: {score_obj.return_current_score_str()}')
        print("---------------")
        print(f'Light Pollution levels: {score_obj.return_current_light_pollution_str()}')
        print("---------------")
        print("Lunar Phase: ",end="")
        WeatherAPI.print_moon_phase(weather_response)
        print("---------------")
        print("Weather Report:")
        print("---------------")
        WeatherAPI.print_weather_report(weather_response)
        print("---------------")

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
                print("Thank You for using the StarSight Application. Live Long and Prosper...")
                resp = "q"
            else:
                print("Please enter either (y) or (n)")
            
    elif resp == "o":
        db.print_rows()
        rows = db.saved_locations()
        flag2 = False
        while flag2 == False: 
            try:
                resp_saved = int(input("Enter ID to select saved location or Enter (0) to return: "))  #catch exception
            except ValueError:
                print("Please enter a valid id ")
                continue
            if resp_saved == 0:
                resp = None
                break
            entry = resp_saved - 1
            if entry < 0 or entry >= len(rows):
                print("entry not found or not in bounds, please re-enter valid entry id")
                continue
            flag2 = True
        print("--------------------------------------------------------------------")
        if resp_saved == 0:
            resp = None
            print("*************************************************************")
            print("*************************************************************")
            continue
        else:
            location_latitude = rows[entry][3]
            location_longitude = rows[entry][2]
 
        city = CityAPI(location_latitude,location_longitude)
        local = city.get_nearby_cities()

        # score calculation/report
        city.city_calculate(score_obj,local)
        weather_response = WeatherAPI.get_weather_response(location_latitude,location_longitude)
        weather_deduction = WeatherAPI.get_weather_score(weather_response)
        
        score_obj.lower_score(weather_deduction)
        print(f'Conditions for StarGazing: {score_obj.return_current_score_str()}')
        print("---------------")
        print(f'Light Pollution levels: {score_obj.return_current_light_pollution_str()}')
        print("---------------")
        print("Lunar Phase: ",end="")
        WeatherAPI.print_moon_phase(weather_response)
        print("---------------")
        print("Weather Report:")
        print("---------------")
        WeatherAPI.print_weather_report(weather_response)
        print("---------------")
        # would you like to continue or not   
        cont_or_stop = None
        while cont_or_stop != "y" and cont_or_stop != "n":
            cont_or_stop = input("Would you like to continue using the application(y)(n)?")
            if cont_or_stop == "y":
                print("*************************************************************")
                print("*************************************************************")
                continue
            elif cont_or_stop == "n":
                print("Thank You for using the StarSight Application. Live Long and Prosper...")
                resp = "q"
            else:
                print("Please enter either (y) or (n)")     
    elif resp == "q":
        print("Thank You for using the StarSight Application. Live Long and Prosper...")
        sys.exit()
    else:
        print("You did not enter a valid option(n)(o)(q)!")
        print("please try again")
        print("*************************************************************")
        print("*************************************************************")
