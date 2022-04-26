# Hobby Site
Site set up to learn Mongodb and to give weather information - especially on air quality for my wife.

## Additional setup
1. Create virtual environment using pipenv install --python 3.9
2. Need to create secrets.py file for secrets - place in api folder
3. need to establish SQLite db - in python shell in route directory run:
```
from app import db 
from api.models import *
db.create_all()
```
4. In termin in route folder run python app.py
5. Go to 127.0.0.1/register to register to login in.  

## Running
Use a web server to run the app. Azure Web Apps manages this for the user. 
