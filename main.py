import git
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'

db = SQLAlchemy(app)


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
