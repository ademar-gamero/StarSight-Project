import git
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
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

@app.route("/learn_more")
def learn_more():
    return render_template("learn_more.html")

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
