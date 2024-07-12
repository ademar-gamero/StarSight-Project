import unittest
import sqlite3
from distance import DB, score
from weather_api import WeatherAPI
import requests
from unittest.mock import patch
import sys

class testDB(unittest.TestCase):
    #TSET FOR DB
    def setUp(self):
        conn = sqlite3.connect('ntest.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # Iterate through the tables and drop each one
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Skip the sqlite_sequence table
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        # Commit the changes and close the connection
        conn.commit()
        self.db = DB("ntest.db") #creates the Database by using the class
        self.db.cur.execute('''CREATE TABLE IF NOT EXISTS saved_locations
                            (name TEXT NOT NULL,
                            longitude TEXT NOT NULL,
                            latitude TEXT NOT NULL)
                            ''')
        self.db.connection.commit()
    def test_saved_locations(self):
        self.assertEqual(self.db.saved_locations(), [])
    def test_add_locations(self):
        a = 45.724115 #latitude
        b = -108.230242 #longitude
        location = ('location', a, b)
        self.db.add_location(location)
        row = self.db.saved_locations()
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0][0], 'location')
        self.assertEqual(float(row[0][2]), a)
        self.assertEqual(float(row[0][1]), b)
    # def test_print_db(self):
    #     row = self.db.saved_locations()
        # if(len(row) == 0):
        #     self.db.print_rows()
        #     mock_print.assert_called_with('No locations have been saved')
        # else:
        #     for rows in row:
        #         print(row)
        #         mock_print.assert_called_with()
class testScore(unittest.TestCase):
    def setUp(self):
        self.sc = score()
    def testing_lower_score(self):
        self.sc.lower_score(7)
        self.assertEqual(self.sc.return_current_score(), 0)
        self.sc.score = 5
        self.sc.lower_score(6)
        self.assertEqual(self.sc.return_current_score(), 0)
        self.sc.score = 5
        self.sc.lower_score(5)
        self.assertEqual(self.sc.return_current_score(), 0)
        self.sc.score = 5
        self.sc.lower_score(0)
        self.assertEqual(self.sc.return_current_score(), 5)
        self.sc.score = 5
        self.sc.lower_score(1)
        self.assertEqual(self.sc.return_current_score(), 4)
    def testing_return_current_score(self):
        self.assertIsInstance(self.sc.return_current_score(), int)
    def test_str_current_score(self):
        self.assertIsInstance(self.sc.return_current_score_str(), str)

class testWeatherAPI(unittest.TestCase):
    def test_point_count(self):
        # testing for 0 points
        self.assertEqual(WeatherAPI.point_count(0), 0)
        self.assertEqual(WeatherAPI.point_count(15), 0)
        self.assertEqual(WeatherAPI.point_count(25), 0)
        # testing for 1 point 
        self.assertEqual(WeatherAPI.point_count(26), 1)
        self.assertEqual(WeatherAPI.point_count(40), 1)
        self.assertEqual(WeatherAPI.point_count(50), 1)
        # testing for 3 points
        self.assertEqual(WeatherAPI.point_count(51), 3)
        self.assertEqual(WeatherAPI.point_count(70), 3)
        self.assertEqual(WeatherAPI.point_count(100), 3)

sys.path.append('../StarSight-Project') # imports python file from parent directory

#page works check
class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///star.db'
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

        self.test_user = User(username='testuser', email='test@example.com', password=generate_password_hash('testpassword'))
        db.session.add(self.test_user)
        db.session.commit()

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
    d
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