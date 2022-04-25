from flask import Flask, render_template, request, flash, redirect, url_for
import pymongo
from api.secrets import mongo_uri, secret_key
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

# basic config
app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key

# database connections
# Cosmos DB
mongodb_client = pymongo.MongoClient(mongo_uri)
content_db = mongodb_client.pebkacsite

# sqlite for users
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_data.db'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# login
login = LoginManager(app)
login.login_view = 'login'

# import other stuff 
import api.models as models
import api.forms as forms

@login.user_loader
def load_user(id):
  return models.User.query.get(int(id))


# routes - move to own file eventually

# login
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return(redirect(url_for('index')))
    else:
        form = forms.LoginForm()
        if form.validate_on_submit():
            user = models.User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Oi try a real username and password!')
                return redirect(url_for('index'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc !='':
                next_page = url_for('index')
            return redirect(next_page)
        return render_template('login.html', title='Sign In', form=form)
'''
# registration 
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        form = forms.RegistrationForm()
        if form.validate_on_submit():
            user = models.User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('You are now a user.')
            return redirect(url_for('login'))
        return render_template('register.html', title='Join this mess', form=form)
'''

#index
@app.route('/')
def index():
    if current_user.is_authenticated:
        page_title = "PEBKAC"
        return render_template('index.html', page_title=page_title)
    else:
        return redirect(url_for('login'))

# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#Asthma Result Sydney
import api.asthmaapp as asthmaapp
@app.route('/<city_name>')
def asthma(city_name):
    if current_user.is_authenticated:
        page_title = f'Air Quality: {city_name}'
        city = asthmaapp.air_pollution_city(city_name, '@12417')
        air_quality = city.aqi_scale()
        return render_template('air_quality.html', air_quality=air_quality, name_city=city.name, page_title=page_title)
    else:
        return redirect(url_for('login'))

#directory of conditions
@app.route('/conditions')
def list_of_cities():
    if current_user.is_authenticated:
        page_title = 'Cities'
        cities = ['Sydney','Stockholm','London','Moscow','Paris','Tokyo','Beijing','Los Angeles','Melbourne','Geelong','Kiama']
        return render_template('list_of_cities.html', page_title=page_title, cities=cities)
    else:
        return redirect(url_for('login'))

# current weather conditions
@app.route('/conditions/<city>')
def conditions(city):
    if current_user.is_authenticated:
        page_title = f'Current weather: {city.title()}'
        #start here get data from models.get_current_conditions(city)
        data = models.get_current_conditions(city.title())
        datetime = models.date_formatter(data['current']['last_updated'])
        return render_template('current_weather.html', page_title=page_title, city=city.title(), data=data, datetime=datetime)
    else:
        return redirect(url_for('login'))

# world map of weather 
@app.route('/conditions/map')
def map():
    if current_user.is_authenticated:
        page_title = "World Map"
        map_json = models.world_map_weather()
        return render_template('weather_map.html', page_title=page_title, map_json=map_json)
    else:
        return redirect(url_for('login'))


# run app
if __name__ == "__main__":
    app.run()