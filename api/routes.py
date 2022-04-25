from app import app, db
from flask import request, render_template, flash, redirect,url_for
from api.models import User
from forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required



#index route
@app.route('/new')
def index():
    page_title = "PEBKAC: where the error is you"
    return render_template('index.html', page_title=page_title)

#Asthma Result Sydney
import asthmaapp as asthmaapp
@app.route('/<city_name>')
def asthma(city_name):
    page_title = f'Air Quality: {city_name}'
    city = asthmaapp.air_pollution_city(city_name, '@12417')
    air_quality = city.aqi_scale()
    return render_template('air_quality.html', air_quality=air_quality, name_city=city.name, page_title=page_title)