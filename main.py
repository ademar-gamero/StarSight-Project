import git
import ast
import json

import asyncio
import aiohttp
import nest_asyncio

from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from inference_sdk import InferenceHTTPClient
from forms import LocationForm, RegistrationForm, AddFriendForm, UploadPhotoForm

from distance import curr_user, score1, CityAPI
from weather_api import WeatherAPI
from constellation import ConstellationCalculator, populate_constellations_table
import secrets
import os


from datetime import datetime
from roboflow import Roboflow
import supervision as sv
import cv2
import numpy as np



nest_asyncio.apply()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'

STATIC_FOLDER = 'static'
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    reviewer_count = db.Column(db.Integer, unique=False, nullable=True)
    address = db.Column(db.String(256),unique=False,nullable=True)
    latitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    longitude = db.Column(db.Numeric(4, 7), unique=False, nullable=False)
    elevation = db.Column(db.Numeric(6, 1), unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shared_with = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return f"Location({self.id},{self.latitude},{self.longitude})"

    def loc_to_dict(self):
        return {
                'id': self.id,
                'name': self.name,
                'address': self.address,
                'rating': float(self.rating) if self.rating else None,
                'reviewer_count': int(self.reviewer_count) if self.reviewer_count else None,
                'latitude': float(self.latitude),
                'longitude': float(self.longitude),
                'elevation': float(self.elevation) if self.elevation else None,
                'shared_with': self.shared_with  # Include shared_with in the dictionary
                }
    
    
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True) #Primary key for Friend table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #Foreign key column linking User tbale, id of user who sent the request
    friend_id = db.Column(db.Integer, nullable=False) #A column for the ID of user who recieved the friend request
    status = db.Column(db.String(20), nullable=True) # 'pending', 'accepted'
    friend = db.relationship('User', backref='friend') #establish relationship to the user, specifically person who received request

    def __repr__(self):
        return f"Friendship('{self.user_id}', '{self.friend_id}', '{self.status}')"


class Constellation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    description = db.Column(Text, nullable=False)
    img = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"Constellation({self.name})"

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.today())
    # foreign keys to reference users and locations
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# password = generate_password_hash("password")


with app.app_context():
    db.create_all()
    if Constellation.query.first() is None:
        populate_constellations_table(db,Constellation)

    address = "testing"
    if Location.query.filter_by(latitude=43.982465, longitude=-89.078786,reviewer_count=5).first() == None:
        test_1 = Location(name="test_db_5",reviewer_count=5,latitude=43.982465,longitude=-89.078786,address=address)
        db.session.add(test_1)
        db.session.commit()

def clear_session():
    session["location"] = []
    session["optimal_locs"] = []

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
    clear_session()
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

#helper method to process a location
async def process_loc(loc,single):

    loc_score = score1()
    city = CityAPI(loc["lat"],loc["lng"])
    local = await city.get_nearby_cities()
    address = await city.retrieve_address()
    await city.city_calculate(loc_score,local)
    await city.calculate_elevation(loc_score)
    weather_response = await WeatherAPI.get_weather_response(loc["lat"],loc["lng"])
    if weather_response is None:
        print("Weather Response was not returned")
        return None
    moon_illum = await WeatherAPI.return_moon_illumination(weather_response)
    moon_deduction = WeatherAPI.calculate_moon_deduction(moon_illum)
    weather_deduction = await WeatherAPI.get_weather_score(weather_response)
    loc_score.lower_score(weather_deduction)
    loc_score.moon_light_pollution -= moon_deduction

    if loc_score.score >= 3 or single == True: #dont forget to change back
       weather_rep = await WeatherAPI.return_weather_report(weather_response)
       lunar_phase = await WeatherAPI.return_moon_phase(weather_response)
       optimal_loc = ({'lat':loc['lat'], 'lng':loc['lng'], 'label':loc['label'], 'ranking':loc_score.return_current_score_str(),'ranking_score':loc_score.score,
                            'light_ranking':loc_score.return_current_light_pollution_str(), 'weather_report':weather_rep,
                       'lunar_phase':lunar_phase, 'lunar_impact':loc_score.moon_light_pollution_card[loc_score.moon_light_pollution], 'address':address})
       return optimal_loc
    return None

@app.route("/find_stars", methods=['GET','POST'])
def find_stars():
    popular_markers = []
    for location in Location.query.filter(Location.reviewer_count >= 5).all():
        popular_markers.append(location.loc_to_dict()) 

    print(popular_markers)
    if len(cur_usr.coords) != 0:
        zoom_coords = {"lat":cur_usr.coords[0],"lng":cur_usr.coords[1]}
    else:
        zoom_coords = {"lat":37.263056,"lng":-115.79302}

    form = LocationForm()
    api_key = os.environ.get('GOOGLE_KEY') 
    map_id = os.environ.get('GOOGLE_ID')
    if request.method == "POST":
       values = request.form.get('selection')
       
       if values != None:
           v_processed = json.loads(values)
           loc_lat = v_processed["lat"]
           loc_lng = v_processed["lng"]
           loc_lat = float(loc_lat)
           loc_lng = float(loc_lng)
           point = {"lat":loc_lat,"lng":loc_lng}
           ovrl_ranking = v_processed["ranking"]
           light_ranking = v_processed["light_ranking"]
           weather_report = v_processed["weather_report"]
           session["weather_report"] = weather_report
           session["location"] = point
           session["address"] = v_processed["address"]
           l_phase = v_processed["lunar_phase"]
           l_score = v_processed["lunar_impact"]
           return redirect(url_for("results",rating=ovrl_ranking,light_rating=light_ranking, lunar_phase=l_phase,lunar_impact=l_score))

       session.pop("optimal_locs",[])

       search_radius = form.loc_radius.data
       lat = request.form.get('lat')
       lng = request.form.get('lng')
       if lat == '' or lng == '':
        flash("Please select a location from the interactive map or enter a valid latitude/longitude manually")
        return render_template("find_stars.html", form=form, map_api_key = api_key,map_id=map_id,usr_coords = zoom_coords,markers=[])

       origin = (lat,lng)
       nearby_locs = cur_usr.calculate_nearby_locs([], origin, search_radius)
       optimal_locs = []
       loop = asyncio.get_event_loop()
       processes = [process_loc(loc=loc,single=False) for loc in nearby_locs]
       results = loop.run_until_complete(asyncio.gather(*processes))
       #print(results)
       optimal_locs = [result for result in results if result is not None]
       #sort with higher results at top
       optimal_locs.sort(key=lambda x: x['ranking_score'],reverse=True)
       '''
       for loc in nearby_locs:
           
           
           loc_score = score1()
           city = CityAPI(loc["lat"],loc["lng"])
           local = city.get_nearby_cities()
           city.city_calculate(loc_score,local)
           city.calculate_elevation(loc_score)
           weather_response = WeatherAPI.get_weather_response(loc["lat"],loc["lng"])
           moon_illum = WeatherAPI.return_moon_illumination(weather_response)
           moon_deduction = WeatherAPI.calculate_moon_deduction(moon_illum)
           weather_deduction = WeatherAPI.get_weather_score(weather_response)
           loc_score.lower_score(weather_deduction)
           loc_score.moon_light_pollution -= moon_deduction
           print(loc_score.score)
           if loc_score.score >= 2:
               weather_rep = WeatherAPI.return_weather_report(weather_response)
               lunar_phase = WeatherAPI.return_moon_phase(weather_response)
               optimal_locs.append({'lat':loc['lat'], 'lng':loc['lng'], 'label':loc['label'], 'ranking':loc_score.return_current_score_str(),'ranking_score':loc_score.score,
                                    'light_ranking':loc_score.return_current_light_pollution_str(), 'weather_report':weather_rep,
                                    'lunar_phase':lunar_phase, 'lunar_impact':loc_score.moon_light_pollution_card[loc_score.moon_light_pollution]})
            '''

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


        return render_template("find_stars.html",form=form, map_api_key = api_key, map_id=map_id ,usr_coords = zoom_coords,markers=optimal_locs, popular_markers=popular_markers)

@app.route("/results/<rating>/<light_rating>/<lunar_phase>/<lunar_impact>",methods=['GET','POST'])
def results(rating,light_rating,lunar_phase,lunar_impact):
    weather_report = session.get("weather_report", [])
    point = session.get("location", None)
    address = session["address"]
    if address == None and point != None:
        calc = CityAPI(point["lat"],point["lng"])
        loc_address = asyncio.run(calc.retrieve_address())
        address = loc_address['results'][0].get('formatted_address') 
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
                           point=point,lunar_impact=lunar_impact)
        name = request.form.get("name")
        if lat and lng and name:
            lat = float(lat)
            lng = float(lng)
            new_loc = Location(name=name,latitude=lat,longitude=lng,address=address,user=current_user)
            db.session.add(new_loc)
            db.session.commit()
            flash("Location Saved successfully")
    return render_template("results.html",rating=rating,light_rating=light_rating, 
                           weather_report=weather_report,lunar_phase=lunar_phase,point=point,lunar_impact = lunar_impact,
                           address=address)
         
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
    locations = []
    user = load_user_from_db(current_user.id)
    if user:
        locations = user.saved_locations
    if locations == []:
        flash("You have no saved locations","light")

    friends = db.session.query(User).filter(
        (User.id == Friend.friend_id) & (Friend.user_id == current_user.id) & (Friend.status == 'accepted') |
        (User.id == Friend.user_id) & (Friend.friend_id == current_user.id) & (Friend.status == 'accepted')
    ).distinct().all()

    return render_template('saved_locations.html', locations=locations, friends=friends)

@app.route('/share_location/<int:location_id>', methods=['POST'])
@login_required
def share_location(location_id):
    friend_id = request.form.get('friend_id')
    location = Location.query.get(location_id)
    if location and friend_id:
        shared_with = location.shared_with.split(',') if location.shared_with else []
        if friend_id not in shared_with:
            shared_with.append(friend_id)
            location.shared_with = ','.join(shared_with)
            db.session.commit()
            flash(f'Location shared with {User.query.get(friend_id).username}!', 'success')
        else:
            flash('Location already shared with this friend.', 'info')
    return redirect(url_for('saved_locations_page'))

@app.route('/saved_locations/remove_saved/<location_id>', methods=['GET','POST'])
def remove_saved_location(location_id):
    location_id = int(location_id)
    location = Location.query.get(location_id)
    display_location = None
    if location:
        display_location = location.loc_to_dict()
    if request.method == 'POST':
        if request.form["answer"] == "yes":
            db.session.delete(location)
            db.session.commit()
            flash("Location successfully removed")
        else:
            flash("Location was not removed")
        return redirect(url_for('saved_locations_page'))
    return render_template('remove_saved.html',location = display_location)

@app.route("/find_constellations/<latitude>/<longitude>")
def find_constellations(latitude,longitude):
    lat = float(latitude)
    lng = float(longitude)
    display_constellations = []
    loc = {"lat":lat,"lng":lng}
    session["location"] = loc
    calc = ConstellationCalculator(loc)
    constellations = calc.find_constellations()
    print(constellations)
    for constellation in constellations:
        print(constellations[constellation])
        if constellations[constellation] >= 7:
            db_constellation = Constellation.query.filter_by(name=constellation).first()
            if db_constellation:
                display_constellations.append({"name":db_constellation.name,"img":db_constellation.img,"description":db_constellation.description})
    return render_template("find_constellations.html", constellations=display_constellations)
             

@app.route('/<latitude>/<longitude>/results')
def calculate_results(latitude, longitude):
    loc = {"lat":latitude,"lng":longitude,"label":1}
    session["location"] = loc
    ranking = None
    light_ranking = None
    lunar_phase = None
    lunar_impact = None
    result = asyncio.run(process_loc(loc=loc,single=True))
    print(result)
    if result is not None:
        ranking = result["ranking"]
        light_ranking = result["light_ranking"]
        lunar_phase = result["lunar_phase"]
        lunar_impact = result["lunar_impact"]
        session["weather_report"] = result["weather_report"]
    '''
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
    '''
    return redirect(url_for("results",rating=ranking,light_rating=light_ranking, lunar_phase=lunar_phase, lunar_impact=lunar_impact))
    #basically sends a POST request for database
    #if successful we send the data into the html file


@app.route('/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            constellations, annotated_image_path = detect_constellations(filepath)
            session['constellations'] = constellations
            session['annotated_image'] = annotated_image_path
            return redirect(url_for('constellation_results'))
    return render_template('upload_photo.html')

@app.route('/constellation_results')
@login_required
def constellation_results():
    constellations = session.get('constellations', [])
    annotated_image = session.get('annotated_image', '')
    return render_template('constellation_results.html', constellations=constellations, annotated_image=annotated_image)

def detect_constellations(filepath):
    rf = Roboflow(api_key="BmaSz5YCzhmjapwU7201")
    project = rf.workspace().project("constellation-dsphi")
    model = project.version(1).model
    result = model.predict(filepath, confidence=40, overlap=30).json()

    boxes = []
    confidences = []
    class_ids = []
    for prediction in result['predictions']:
        x, y, w, h = prediction['x'], prediction['y'], prediction['width'], prediction['height']
        boxes.append([x - w/2, y - h/2, x + w/2, y + h/2])
        confidences.append(prediction['confidence'])
        class_ids.append(prediction['class_id'])
    detections = sv.Detections(
        xyxy=np.array(boxes),
        confidence=np.array(confidences),
        class_id=np.array(class_ids)
    )
    labels = [item["class"] for item in result["predictions"]]
    label_annotator = sv.LabelAnnotator()
    box_annotator = sv.BoxAnnotator()
    image = cv2.imread(filepath)
    annotated_image = box_annotator.annotate(scene=image, detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)
    
    annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "annotated_" + os.path.basename(filepath))
    cv2.imwrite(annotated_image_path, annotated_image)
    
    return labels, "uploads/annotated_" + os.path.basename(filepath)

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

    # Fetch locations shared with the current user
    shared_locations_data = []
    shared_locations = Location.query.filter(Location.shared_with.like(f"%{current_user.id}%")).all()
    for location in shared_locations:
        sharer_users = User.query.filter(User.saved_locations.contains(location)).all()
        sharers = ', '.join([user.username for user in sharer_users])
        shared_locations_data.append({
            'location': location,
            'sharers': sharers
        })

    return render_template('friends.html', form=form, friends=friends,
                           pending_user_requests=pending_user_requests, shared_locations_data=shared_locations_data)

@app.route('/accept_friend/<int:friend_id>')
@login_required
def accept_friend(friend_id):
    friend_requests = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.id, status='pending').first()
    if friend_requests:
        friend_requests.status = 'accepted'
        db.session.commit()
        flash('Friend request accepted!', 'success')
    return redirect(url_for('friends'))

@app.route('/decline_friend/<int:friend_id>')
@login_required
def decline_friend(friend_id):
    friend_request = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.id, status='pending').first()
    if friend_request:
        db.session.delete(friend_request)
        db.session.commit()
        flash('Friend request declined.', 'success')
    return redirect(url_for('friends'))


    return redirect(url_for('friends'))

@app.route('/save_shared_location/<int:location_id>', methods=['POST'])
@login_required
def save_shared_location(location_id):
    location = Location.query.get(location_id)
    if location:
        new_location = Location(
            name=location.name,
            rating=location.rating,
            reviewer_count=location.reviewer_count,
            address=location.address,
            latitude=location.latitude,
            longitude=location.longitude,
            elevation=location.elevation,
            user_id=current_user.id
        )
        db.session.add(new_location)
        # Remove the user ID from the shared_with list
        shared_with_list = location.shared_with.split(',')
        shared_with_list.remove(str(current_user.id))
        location.shared_with = ','.join(shared_with_list) if shared_with_list else None
        db.session.commit()
        flash('Location saved to your saved locations!', 'success')
    return redirect(url_for('friends'))

@app.route('/remove_shared_location/<int:location_id>', methods=['POST'])
@login_required
def remove_shared_location(location_id):
    location = Location.query.get(location_id)
    if location:
        # Remove the user ID from the shared_with list
        shared_with_list = location.shared_with.split(',')
        shared_with_list.remove(str(current_user.id))
        location.shared_with = ','.join(shared_with_list) if shared_with_list else None
        db.session.commit()
        flash('Location removed from shared locations.', 'success')
    return redirect(url_for('friends'))

# reviews code
# TODO: make reviews dynamic for locations
@app.route('/reviews/<marker_id>')
def reviews(marker_id):
    reviews = Reviews.query.filter_by(location_id=int(marker_id)).order_by(Reviews.date.desc()).all()
    return render_template('reviews.html', reviews=reviews)


@app.route('/submit_review/<marker_id>', methods=['POST'])
def submit_review(marker_id):
    rating = int(request.form['rating'])
    comment = request.form['comment']
    new_review = Reviews(rating=rating, comment=comment, location_id=int(marker_id))
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('review'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

