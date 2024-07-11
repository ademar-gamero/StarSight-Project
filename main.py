import git
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from forms import LocationForm, RegistrationForm
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

secret = secrets.token_urlsafe(16)
app.config['SECRET_KEY'] = secret

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

@app.route("/")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #user = User.query.filter_by(username=username).first()  # Query the User model by username
        #if user and check_password_hash(user.password, password):  # Check if user exists and password matches
        #possible syntax to retrieve users data from db

        if username == 'admin' and password == 'password': # For testing purposes
            return render_template("main_menu.html")  # Redirect to main menu on successful login
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')  # Render the login template on GET request or failed login

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
    return render_template('saved_locations.html', locations=locations)


@app.route('/<int:location.id>/results')
def display_results(id):
    #basically sends a POST request for database
    #if successful we send the data into the html file
    return "Return"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
