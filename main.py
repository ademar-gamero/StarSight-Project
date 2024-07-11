import git
import ast
import json
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
<<<<<<< HEAD
=======
from werkzeug.security import generate_password_hash,check_password_hash

>>>>>>> 92271be2afb4946e7b0ba9eb743bd271b3c1285a
from forms import LocationForm, RegistrationForm
from distance import curr_user, score1, CityAPI
from weather_api import WeatherAPI
import secrets
import os



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

cur_usr = curr_user()
sec = secrets.token_urlsafe(16)
app.secret_key = sec

secret = secrets.token_urlsafe(16)
app.config['SECRET_KEY'] = secret

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    saved_locations = db.relationship('Location', backref='user')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    state = db.Column(db.String(20), unique=False, nullable=True)
    county = db.Column(db.String(20), unique=False, nullable=True)
    latitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    longitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    elevation = db.Column(db.Numeric(6, 1), unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Location('{self.id},'{self.latitude}',{self.longitude})"


password = generate_password_hash("password")

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user_from_db(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()  # Query the User model by username
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main_menu'))  # Redirect to main menu on successful login
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')  # Render the login template on GET request or failed login

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/main_menu")
@login_required
def main_menu():
    return render_template("main_menu.html")

@app.route("/create_account", methods=['GET', 'POST'])
def register():
    username = None
    password = None
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = None
        if form.password.data != None:
            hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=None, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created you can now login!')
        return redirect(url_for('login'))

    return render_template("account_creation.html",
                           form = form,
                           username = username,
                           password = password)

@app.route("/learn_more")
def learn_more():
    return render_template("learn_more.html")

@app.route("/find_stars", methods=['GET','POST'])
def find_stars():
    form = LocationForm()
    api_key = os.environ.get('GOOGLE_KEY') 
    if request.method == "POST":
       msg = None
       values = request.form.get('selection')
       if values != None:
           v_processed = json.loads(values)
           loc_lat = v_processed["lat"]
           loc_lng = v_processed["lng"]
           loc_lat = float(loc_lat)
           loc_lng = float(loc_lng)
           point = [loc_lat,loc_lng]
           ovrl_ranking = v_processed["ranking"]
           light_ranking = v_processed["light_ranking"]
           weather_report = v_processed["weather_report"]
           session["weather_report"] = weather_report
           session["location"] = point
           l_phase = v_processed["lunar_phase"]
           return redirect(url_for("results",rating=ovrl_ranking,light_rating=light_ranking, lunar_phase=l_phase))
       else:
           msg = "We did not find any suitable places for star gazing in your area"
       search_radius = form.loc_radius.data
       lat = request.form.get('lat')
       lng = request.form.get('lng')
       if lat == '' or lng == '':
        return render_template("find_stars.html", form=form, map_api_key = api_key,usr_coords = cur_usr.coords,markers=[],msg="Please select a point or enter a point from the map")
       origin = (lat,lng)
       nearby_locs = cur_usr.calculate_nearby_locs([], origin, search_radius)
       optimal_locs = []
       for loc in nearby_locs:
           loc_score = score1()
           city = CityAPI(loc["lat"],loc["lng"])
           local = city.get_nearby_cities()
           city.city_calculate(loc_score,local)
           weather_response = WeatherAPI.get_weather_response(loc["lat"],loc["lng"])
           weather_deduction = WeatherAPI.get_weather_score(weather_response)
           loc_score.lower_score(weather_deduction)
           if loc_score.score >= 3:
               weather_rep = WeatherAPI.return_weather_report(weather_response)
               lunar_phase = WeatherAPI.return_moon_phase(weather_response)
               optimal_locs.append({'lat':loc['lat'], 'lng':loc['lng'], 'label':loc['label'], 'ranking':loc_score.return_current_score_str(),
                                    'light_ranking':loc_score.return_current_light_pollution_str(), 'weather_report':weather_rep,
                                    'lunar_phase':lunar_phase})

       return render_template("find_stars.html", form=form, map_api_key = api_key,usr_coords = origin,markers=optimal_locs,msg=msg)
    else:
        return render_template("find_stars.html",form=form, map_api_key = api_key,usr_coords = cur_usr.coords,markers=[],msg=None)

@app.route("/results/<rating>/<light_rating>/<lunar_phase>",methods=['GET','POST'])
@login_required
def results(rating,light_rating,lunar_phase):
    weather_report = session.get("weather_report", [])
    point = session.get("location", [])
    if request.method == "POST":
        lat = request.form.get("hidden_lat")
        lng = request.form.get("hidden_lng")
        user = load_user_from_db(current_user.id)
        locations = []
        if user:
            locations = user.saved_locations
        for loc in locations:
            loc_lat = loc.latitude
            loc_lng = loc.longitude
            if str(loc_lat) == lat and str(loc_lng) == lng:
                flash("This location is already saved in the database, error")
                return render_template("results.html",rating=rating,light_rating=light_rating,weather_report=weather_report,lunar_phase=lunar_phase,
                           point=point)
        name = request.form.get("name")
        if lat and lng and name:
            lat = float(lat)
            lng = float(lng)
            new_loc = Location(name=name,latitude=lat,longitude=lng,user=current_user)  
            db.session.add(new_loc)
            db.session.commit()
        flash("Location Saved successfully")
    return render_template("results.html",rating=rating,light_rating=light_rating,weather_report=weather_report,lunar_phase=lunar_phase,
                           point=point)
         
@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/StarSight/StarSight-Project')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400
      
<<<<<<< HEAD
@app.route('/saved_locations', methods=['GET', 'POST'])
def saved_locations():
    if request.method == 'POST':
        state = request.form['state']
        county = request.form['county']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        location = Location(state=state, county=county, latitude=latitude, longitude=longitude, user_id=current_user.id)
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('saved_locations'))
    
    locations = current_user.saved_locations
    return render_template('saved_locations.html', locations=locations)
    @app.route('/saved_locations')

 #def saved_locations():
  #  user_id = 1  # Replace with your actual user ID logic (e.g., current user ID)
#user = User.query.get(user_id)
   # locations = user.saved_locations
=======
@app.route('/saved_locations')
@login_required
def saved_locations_page():
    #may return multiple users
    #get user id first, then saved locations
    locations=[]
    user = load_user_from_db(current_user.id)
    if user:
        locations= user.saved_locations
>>>>>>> 92271be2afb4946e7b0ba9eb743bd271b3c1285a
    return render_template('saved_locations.html', locations=locations)


<<<<<<< HEAD
@app.route('/<int:location.id>/results')
def display_results(id):
=======

@app.route('/<latitude>/<longitude>/results')
def calculate_results(latitude, longitude):
    loc = (latitude,longitude)
    session["location"] = loc
    loc_score = score1()
    city = CityAPI(latitude,longitude)
    local = city.get_nearby_cities()
    city.city_calculate(loc_score,local)
    weather_response = WeatherAPI.get_weather_response(latitude,longitude)
    weather_deduction = WeatherAPI.get_weather_score(weather_response)
    loc_score.lower_score(weather_deduction)
    weather_rep = WeatherAPI.return_weather_report(weather_response)
    session["weather_report"] = weather_rep
    lunar_phase = WeatherAPI.return_moon_phase(weather_response)
    ranking = loc_score.return_current_score_str()
    light_ranking = loc_score.return_current_light_pollution_str()
    return redirect(url_for("results",rating=ranking,light_rating=light_ranking, lunar_phase=lunar_phase))
>>>>>>> 92271be2afb4946e7b0ba9eb743bd271b3c1285a
    #basically sends a POST request for database
    #if successful we send the data into the html file
    return "Return"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
