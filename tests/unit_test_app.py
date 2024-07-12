#StarSight-Project/astronomy-api.py
import git
import ast
import json
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
import sys
import unittest
import sqlite3

app = Flask(__name__)

sys.path.append('../StarSight-Project') # imports python file from parent directory

#page works check
class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'
        db = SQLAlchemy(app)
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

        self.test_user = User(username='testuser', email='test@example.com', password=generate_password_hash('testpassword'))
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
    ###############
    #### tests ####
    ###############

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_find_stars_page(self):
        response = self.app.get('/find_stars', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_saved_locations_page(self):
        response = self.app.get('/saved_locations', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_results_page(self):
        latitude = 123.456 
        longitude = 78.910 
        lunar_phase = "Full Moon"

        lat_str = str(latitude)
        long_str = str(longitude)
        lunar_phase_str = lunar_phase.replace(' ', '%20')
        response = self.app.get(f'/{lat_str}/{long_str}/results', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    #login and registration checks
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

    #Tests if registration works
    def test_valid_user_registration(self):
        response = self.register('testuser', 'testuser@example.com', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)

        # Check if the user is actually in the database
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'testuser@example.com')


    #Invalid email check
    def test_invalid_email_registration(self):
        response = self.register('testuser2', 'invalid-email', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email address.', response.data)

        # Check that the user is not in the database
        user = User.query.filter_by(username='testuser2').first()
        self.assertIsNone(user)

    #Test logins
    def test_login_success(self):
        # Test successful login
        response = self.login('testuser', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        # Test login failure with incorrect password
        response = self.login('testuser', 'WrongPassword')
        self.assertEqual(response.status_code, 200)

    #Saved Location test
    def test_location_saving(self):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            new_location = Location(name='Test Location', latitude=123.456, longitude=78.910, user=user)
            db.session.add(new_location)
            db.session.commit()

            saved_location = Location.query.filter_by(name='Test Location').first()
            self.assertIsNotNone(saved_location)
            self.assertEqual(saved_location.latitude, 123.456)
            self.assertEqual(saved_location.longitude, 78.910)


if __name__ == "__main__":
    unittest.main()