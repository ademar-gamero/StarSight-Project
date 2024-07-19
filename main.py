import git
import ast
import json
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash

from forms import LocationForm, RegistrationForm, AddFriendForm
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
    name = db.Column(db.String(30), unique=False, nullable=True)
    rating = db.Column(db.Numeric(4, 7), unique=True, nullable=True)
    reviewers = db.Column(db.Integer, unique=False, nullable=True)
    state = db.Column(db.String(20), unique=False, nullable=True)
    county = db.Column(db.String(20), unique=False, nullable=True)
    latitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    longitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    elevation = db.Column(db.Numeric(6, 1), unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Location('{self.id},'{self.latitude}',{self.longitude})"

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True) #Primary key for Friend table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #Foreign key column linking User tbale, id of user who sent the request
    friend_id = db.Column(db.Integer, nullable=False) #A column for the ID of user who recieved the friend request
    status = db.Column(db.String(20), nullable=True) # 'pending', 'accepted'
    friend = db.relationship('User', backref='friend') #establish relationship to the user, specifically person who received request

    def __repr__(self):
        return f"Friendship('{self.user_id}', '{self.friend_id}', '{self.status}')"


password = generate_password_hash("password")

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user_from_db(user_id):
    return User.query.get(int(user_id))

@app.after_request
def add_header(response):
    """
    Add headers to force fresh content and prevent caching.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
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
    
    if len(cur_usr.coords) != 0:
        zoom_coords = {"lat":cur_usr.coords[0],"lng":cur_usr.coords[1]}
    else:
        zoom_coords = {"lat":37.263056,"lng":-115.79302}
    form = LocationForm()
    api_key = os.environ.get('GOOGLE_KEY') 
    if request.method == "POST":
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
       session.pop("optimal_locs",[])
       search_radius = form.loc_radius.data
       lat = request.form.get('lat')
       lng = request.form.get('lng')
       if lat == '' or lng == '':
        flash("Please select a location from the interactive map or enter a valid latitude/longitude manually")
        return render_template("find_stars.html", form=form, map_api_key = api_key,usr_coords = zoom_coords,markers=[])
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
       session['optimal_locs'] = optimal_locs
       if optimal_locs == []:
           flash("We didnt find any suitable locations for viewing stars nearby, consider making your radius bigger")
       return redirect(url_for("find_stars"))
    else:
        optimal_locs = session.get('optimal_locs', [])
        if optimal_locs == []:
            pass
        else:
            zoom_coords = optimal_locs[0] 
        return render_template("find_stars.html",form=form, map_api_key = api_key,usr_coords = zoom_coords,markers=optimal_locs)

@app.route("/results/<rating>/<light_rating>/<lunar_phase>",methods=['GET','POST'])
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
    return render_template("results.html",rating=rating,light_rating=light_rating, weather_report=weather_report,lunar_phase=lunar_phase,point=point)
         
@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/StarSight/StarSight-Project')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400
      
@app.route('/saved_locations')
@login_required
def saved_locations_page():
    #may return multiple users
    #get user id first, then saved locations
    locations=[]
    user = load_user_from_db(current_user.id)
    if user:
        locations= user.saved_locations
    if locations==[]:
        flash("You have no saved locations","light")
    return render_template('saved_locations.html', locations=locations)

#implementing later
#@app.route('/save_location')
#def save_location():
    #redirect url after saving location it goes to the saved location saved_locations_page
    #return redirect(url_for('saved_locations'))


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
    #basically sends a POST request for database
    #if successful we send the data into the html file

@app.route('/friends', methods=["GET", "POST"])
@login_required
def friends():
    form = AddFriendForm()
    if form.validate_on_submit():
        friend = User.query.filter_by(username=form.friend_username.data).first()
        if friend and friend.id != current_user.id:
            existing_friendship = Friend.query.filter_by(user_id=current_user.id, friend_id=friend.id).first()
            if not existing_friendship:
                new_friend = Friend(user_id=current_user.id, friend_id=friend.id, status="pending")
                db.session.add(new_friend)
                db.session.commit()
                flash('Friend request sent!', 'success')
            else:
                flash('Friend request already exists!', 'danger')
        else:
            flash('User not found or trying to friend yourself.', 'danger')

    pending_requests = Friend.query.filter_by(friend_id=current_user.id, status='pending').all()

    # Fetching friends in both directions
    friends = db.session.query(User).filter(
        (User.id == Friend.friend_id) & (Friend.user_id == current_user.id) & (Friend.status == 'accepted') |
        (User.id == Friend.user_id) & (Friend.friend_id == current_user.id) & (Friend.status == 'accepted')
    ).distinct().all()

    pending_user_requests = [(User.query.get(req.user_id), req) for req in pending_requests]
    return render_template('friends.html', form=form, friends=friends,
                           pending_user_requests=pending_user_requests)

@app.route('/accept_friend/<int:friend_id>')
@login_required
def accept_friend(friend_id):
    friend_requests = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.id, status='pending').first()
    current_user_req = Friend.query.filter_by(user_id=current_user.id, friend_id=friend_id, status='pending').first()
    if friend_requests:
        friend_requests.status = 'accepted'
        current_user_req.status = 'accepted'
        db.session.commit()
        flash('Friend request accepted!', 'success')
    return redirect(url_for('friends'))

@app.route('/decline_friend/<int:friend_id>')
@login_required
def decline_friend(friend_id):
    friend_request = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.id, status='pending').first()
    current_user_req = Friend.query.filter_by(user_id=current_user.id, friend_id=friend_id, status='pending').first()
    if friend_request:
        friend_request.status = 'declined'
        current_user_req.status = 'declined'
        db.session.commit()
        flash('Friend request declined.', 'success')
        #this pops up on log in page, after logging out
    return redirect(url_for('friends'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
