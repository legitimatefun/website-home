from werkzeug.security import generate_password_hash, check_password_hash # can use bcrypt-flask
from app import db, login
from flask_login import UserMixin
from app import content_db
from datetime import datetime
from api.secrets import map_box_token

# plotly and pandas imports 
import pandas as pd
from pandas import json_normalize 
from bson import json_util
import json
from pymongo import DESCENDING
import plotly.express as px
import plotly

# conditions collection data
conditions = content_db.real_time_conditions

# map box token for worl_map_weather function
token = map_box_token

# date formatting tool 
def date_formatter(raw_date):
  raw_format = format = "%Y-%m-%d %H:%M"
  dt_object = datetime.strptime(raw_date, raw_format)
  format = "%l:%M %P on %d %b %Y"
  date = dt_object.strftime(format)
  return date 

# user class - for login 
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(20))

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)
  
  def __repr__(self):
    return f'<User: {self.username}>'


# function to get requested city weather data
def get_current_conditions(city):
  match_stage = {"$match": {"location.name":city}}
  project_stage = { "$project": {"id":0, 
                      "current.last_updated":1, 
                      "current.temp_c":1, 
                      "current.condition.text": 1, 
                      "current.condition.icon": 1, 
                      "current.feelslike_c": 1,
                      "current.air_quality.gb-defra-index": 1}
                      }
  sort_stage = { "$sort": {"current.last_updated": -1}}
  limit_stage = { "$limit": 1}
  pipeline = [match_stage, project_stage, sort_stage, limit_stage]
  response = conditions.aggregate(pipeline)
  result = response.next() # converts response into python dict
  return result 

# function to produce world map with weather for selected cities
def world_map_weather():
  # get result from each city
  # use aggregation method with pipeline
  pipeline = [
      {"$unwind": "$location.name"}, # unwinds docs in database so new doc with requested fields can be returned
      # fields needed for map for each city
      {"$project": {"_id":0, "location.name":1, 
                    "current.last_updated":1, 
                    "location.lat":1, 
                    "location.lon":1, 
                    "current.temp_c":1, 
                    "current.feelslike_c":1, 
                    "current.condition.text":1, 
                    "current.humidity":1, 
                    "current.air_quality.us-epa-index":1}}, 
      {"$sort": {"current.last_updated_epoch": DESCENDING }}, # sorts all records by last update epoch time. As all other times in local time zones this is the best way to sort results. Grab all records because faster to slice dataframe then to use $limit in aggregation.
  ]
  weather_data = conditions.aggregate(pipeline) 
  # loads the data as json
  sanitised = json.loads(json_util.dumps(weather_data))
  # un-nests the data
  normalised = json_normalize(sanitised)
  # makes dataframe
  df = pd.DataFrame(normalised)
  # slicing to get last 13 records (one for each city) - quicker to slice than to use $limit in aggregation
  df_short = df.tail(13).copy()
  # new column to make dots bigger on map - plotly uses column for this - see below
  df_short['size'] = [x*2/x for x in range(1,14)]
  # new columns to split date from time - helps with readability in final map
  df_short['Date (local)'] = pd.to_datetime(df_short['current.last_updated']).dt.date 
  df_short['Time (local)'] = pd.to_datetime(df_short['current.last_updated']).dt.time
  # rename existing columns for plot
  df_short.rename(columns={"current.temp_c":"Temp °C", 
                          "current.feelslike_c":"Feels like °C",
                          "current.condition.text":"Conditions",
                          "current.humidity":"Humidity %",
                          "current.air_quality.us-epa-index":"EPA air quality",},
                          inplace=True)
  # create map 
  fig = px.scatter_mapbox(df_short, 
                        lat="location.lat", 
                        lon="location.lon", 
                        hover_name="location.name", 
                        hover_data={"Temp °C":True, "Feels like °C":True, "EPA air quality":True, "Humidity %":True, "Date (local)":True, "Time (local)":True, "location.lon":False, "location.lat":False, "size":False},
                        color_discrete_sequence=["pink"], 
                        zoom=1, 
                        height=600, 
                        width=1000, 
                        center={'lat':15.455060, 'lon':148.871616},
                        size='size',
                        opacity=0.5
                        )
  # setting style and margins
  fig.update_layout(mapbox_style="satellite-streets", mapbox_accesstoken = token)
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})  
  # encode to json and return 
  map_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
  return map_json 




