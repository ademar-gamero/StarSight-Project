import git
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from forms import LocationForm
from distance import curr_user, score, CityAPI
from weather_api import WeatherAPI
import secrets
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'

db = SQLAlchemy(app)
cur_usr = curr_user()
sec = secrets.token_urlsafe(16)
app.secret_key = sec

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    saved_locations = db.relationship('Location',backref='user')
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    state = db.Column(db.String(20), unique=False, nullable=False)
    county = db.Column(db.String(20), unique=False, nullable=False)
    latitude = db.Column(db.Numeric(4,7), unique=False,nullable=False)
    longitude = db.Column(db.Numeric(4,7), unique=False,nullable=False)
    elevation = db.Column(db.Numeric(6,1), unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f"Location('{self.id}', '{self.user_id.username}','{self.state}')"

with app.app_context():
    db.create_all()

@app.route("/")
def main_menu():
    return "<h1> StarSight Application version 1.0 </h1>"

@app.route("/find_stars", methods=['GET','POST'])
def find_stars():
    form = LocationForm()
    api_key = os.environ.get('GOOGLE_KEY') 
    if request.method == "POST":
       score = request.form.get('selection')
       if score != None:
           return redirect(url_for("results",point=score))
       search_radius = form.loc_radius.data
       lat = request.form.get('lat')
       lng = request.form.get('lng')
       if lat == '' or lng == '':
        return render_template("find_stars.html", form=form, map_api_key = api_key,usr_coords = cur_usr.coords,markers=[],msg="Please select a point or enter a point from the map")
       origin = (lat,lng)
       nearby_locs = cur_usr.calculate_nearby_locs([], origin, search_radius)
       optimal_locs = []
       for loc in nearby_locs:
           loc_score = score()
           city = CityAPI(loc["lat"],loc["lng"])
           local = city.get_nearby_cities()
           city.city_calculate(loc_score,local)
           weather_response = WeatherAPI.get_weather_response(loc["lat"],loc["lng"])
           weather_deduction = WeatherAPI.get_weather_score(weather_response)
           loc_score.lower_score(weather_deduction)
           if loc_score.score >= 3:
               optimal_locs.append(loc)

       return render_template("find_stars.html", form=form, map_api_key = api_key,usr_coords = origin,markers=optimal_locs,msg=None)
    else:
        return render_template("find_stars.html",form=form, map_api_key = api_key,usr_coords = cur_usr.coords,markers=[],msg=None)

@app.route("/results")
def results(point):
    return render_template("results.html",ovr_rating=point,light_rating=point)
         
@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/StarSight/StarSight-Project')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
