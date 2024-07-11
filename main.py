import git
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LocationForm, RegistrationForm
from distance import curr_user, score, CityAPI
from weather_api import WeatherAPI
import secrets
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'

# db = SQLAlchemy(app)
# cur_usr = curr_user()
# sec = secrets.token_urlsafe(16)
# app.secret_key = sec
#
# secret = secrets.token_urlsafe(16)
# app.config['SECRET_KEY'] = secret

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    saved_locations = db.relationship('Location', backref='user')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(20), unique=False, nullable=False)
    county = db.Column(db.String(20), unique=False, nullable=False)
    latitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    longitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    elevation = db.Column(db.Numeric(6, 1), unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Location('{self.id}', '{self.user_id.username}','{self.state}')"


with app.app_context():
    db.create_all()

    # Create test user
    test_user = User(username='testuser', email='testuser@example.com', password=secrets.token_urlsafe(16))
    db.session.add(test_user)
    db.session.commit()

    # Create test locations
    test_location1 = Location(state='California', county='Los Angeles', latitude=34.0522, longitude=-118.2437, elevation=89, user_id=test_user.id)
    test_location2 = Location(state='California', county='San Francisco', latitude=37.7749, longitude=-122.4194, elevation=16, user_id=test_user.id)

    db.session.add(test_location1)
    db.session.add(test_location2)
    db.session.commit()

@app.route("/")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hardcoded username and password for testing
        if username == 'admin' and password == 'password':
            user = User.query.filter_by(username='testuser').first()
            if user:
                flash('Login successful!', 'success')
                return render_template('saved_locations.html', user_id=user.id)
        flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')


@app.route("/main_menu")
def main_menu():
    return render_template("main_menu.html")

@app.route("/create_account", methods=['GET', 'POST'])
def register():
    username = None
    password = None
    form = RegistrationForm()

    if form.validate_on_submit():
        User.username = form.username.data
        User.password = form.password.data
        form.username.data = ''
        form.password.data = ''

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
      
@app.route('/save_location', methods=['POST'])
def saved_locations_page(user_id):
    user = User.query.get(user_id)
    locations = user.saved_locations
    return render_template('saved_locations.html', locations=locations, user_id=user_id)

@app.route('/<int:id>/results')
def display_results(user_id, id):
    #basically sends a POST request for database
    #if successful we send the data into the html file
    location = Location.query.get_or_404(id)
    return render_template('results.html', location=location, user_id=user_id)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
