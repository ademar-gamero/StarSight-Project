import requests
import aiohttp
import aiohttp
import json
import os

class WeatherAPI:

    # Method which returns points based on the average cloud coverage percentage
    @staticmethod
    def point_count(avg):
        if avg >= 0 and avg <= 25:
            return 0
        elif avg > 25 and avg <= 50:
            return 1
        else:
            return 3


    # calculates and returns average percentage of cloud coverage
    @staticmethod
    async def get_weather_score(response):
        cloud_cov_avg = 0
        for i in range(22, 24):
            curr = response['forecast']['forecastday'][0]['hour'][i]
            cloud_cov_avg += curr['cloud']
        for i in range(0, 4):
            curr = response['forecast']['forecastday'][1]['hour'][i]
            cloud_cov_avg += curr['cloud']
        new_cloud_avg = cloud_cov_avg / 6
        val = WeatherAPI.point_count(new_cloud_avg)
        return val


    # get just the weather report
    @staticmethod
    async def print_weather_report(response):
        for i in range(22, 24):
            curr = response['forecast']['forecastday'][0]['hour'][i]
            print(curr['time'], curr['condition']['text'])
        for i in range(0, 4):
            curr = response['forecast']['forecastday'][1]['hour'][i]
            print(curr['time'], curr['condition']['text'])
    
    @staticmethod
    async def return_weather_report(response):
        weather_report = []
        for i in range(22, 24):
            curr = response['forecast']['forecastday'][0]['hour'][i]
            weather_report.append((curr['time'], curr['condition']['text']))
        for i in range(0, 4):
            curr = response['forecast']['forecastday'][1]['hour'][i]
            weather_report.append((curr['time'], curr['condition']['text']))
        return weather_report

    # called from main
    @staticmethod
    async def print_moon_phase(response):
        moon_phase = response['forecast']['forecastday'][0]['astro']['moon_phase'] 
        print(moon_phase)

        # left in case of incorporation
        # moon_illumination = response['forecast']['forecastday'][0]['astro']['moon_illumination']

    @staticmethod
    async def return_moon_illumination(response):
        moon_illumination = response['forecast']['forecastday'][0]['astro']['moon_illumination']
        print(moon_illumination)
        return moon_illumination

    @staticmethod
    def calculate_moon_deduction(moon_illum):
        if 75 > moon_illum > 45:
            return 1
        elif moon_illum >= 75:
            return 2
        elif moon_illum < 45:
            return 0

    @staticmethod
    async def return_moon_phase(response):
        moon_phase = response['forecast']['forecastday'][0]['astro']['moon_phase'] 
        return moon_phase

    # Called by main class
    # Makes call to API forecast data based on location
    # returns response
    @staticmethod
    async def get_weather_response(latitude,longitude):
        print(latitude)
        print(longitude)
    @staticmethod
    async def get_weather_response(latitude,longitude):
        print(latitude)
        print(longitude)
        my_api_key = os.getenv('API_KEY')
        url = "http://api.weatherapi.com/v1//forecast.json"
        location = f"{latitude},{longitude}"
        params = {
                  'key': my_api_key,
                  'q': location,
                  'days': '2'
                  }
        async with aiohttp.ClientSession() as session:
            async with session.get(url,params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'error' in data:
                        print(data['error']['message'])
                        return None
                    return data
                else:
                    print(f"Error: HTTP {response.status}")
                    return None
        location = f"{latitude},{longitude}"
        params = {
                  'key': my_api_key,
                  'q': location,
                  'days': '2'
                  }
        async with aiohttp.ClientSession() as session:
            async with session.get(url,params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'error' in data:
                        print(data['error']['message'])
                        return None
                    return data
                else:
                    print(f"Error: HTTP {response.status}")
                    return None
