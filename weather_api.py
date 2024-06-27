import requests
import json
import os

class WeatherAPI:
    def point_count(avg):
        if avg >= 0 and avg <= 25:
            return 0
        
        elif avg > 25 and avg <= 50:
            return 1
        
        else:
            return 3


    def print_forecast(response):
        cloud_cov_avg = 0

        for i in range(20, 24):
            curr = response['forecast']['forecastday'][0]['hour'][i]
            print(curr['time'], curr['condition']['text'])
            cloud_cov_avg += curr['cloud']

        for i in range(0, 4):
            curr = response['forecast']['forecastday'][1]['hour'][i]
            print(curr['time'], curr['condition']['text'])
            cloud_cov_avg += curr['cloud']

        return cloud_cov_avg / 8
        

    def get_weather(latitude, longitude):
        my_api_key = os.getenv('API_KEY')

        url="http://api.weatherapi.com/v1//forecast.json"

        location = str(latitude) + "," + str(longitude) 

        response = requests.post(url, {
                                        'key': my_api_key,
                                        'q': location,
                                        'days': '2'
                                      })

        response = response.json()

        cloud_cov_avg = WeatherAPI.print_forecast(response)

        return WeatherAPI.point_count(cloud_cov_avg)
    
# Testing
# latitude = 31.772543
# longitude = -106.460953
# WeatherAPI.get_weather(latitude, longitude)
