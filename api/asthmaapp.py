# Script to generate air quality result

import requests

from api.secrets import aqicn_key as aqicn_key

class air_pollution_city:
    def __init__(self, name, uid, aqi_number=None): #uid is the unique ID for each station: https://aqicn.org/json-api/doc/
        self.name = name
        self.uid = uid
        self.aqi_number = aqi_number
    
    # gets AQI number from end point
    def set_aqi_number(self):
        payload = requests.get('http://api.waqi.info/feed/'+self.uid+'/?', params=aqicn_key)
        data = payload.json()
        new_aqi_number = data['data']['aqi']
        self.aqi_number = new_aqi_number
        return new_aqi_number
    
    # converts AQI number to scale 
    def aqi_scale(self):
        self.set_aqi_number()
        if type(self.aqi_number) is int:
            if self.aqi_number < 50:
                scale = 'Good'
            elif self.aqi_number < 100:
                scale = 'Moderate'
            elif self.aqi_number < 150:
                scale = 'Unhealthy for Sensitive Groups'
            elif self.aqi_number < 200:
                scale = 'Unhealthy'
            elif self.aqi_number < 300:
                scale = 'Very Unhealthy'
            elif self.aqi_number >= 300:
                scale = 'Hazardous'
        else:
            scale = 'no data'
        return scale