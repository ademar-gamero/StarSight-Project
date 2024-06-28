import unittest
import sqlite3
from distance import DB, score
import requests
from unittest.mock import patch

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
    def setUp(self):
        self.wAPI = WeatherAPI()
    def test_point_count(self):
        # testing for 0 points
        self.assertEqual(self.wAPI.point_count(0), 0)
        self.assertEqual(self.wAPI.point_count(15), 0)
        self.assertEqual(self.wAPI.point_count(25), 0)
        # testing for 1 point 
        self.assertEqual(self.wAPI.point_count(26), 1)
        self.assertEqual(self.wAPI.point_count(40), 1)
        self.assertEqual(self.wAPI.point_count(50), 1)
        # testing for 3 points
        self.assertEqual(self.wAPI.point_count(51), 3)
        self.assertEqual(self.wAPI.point_count(70), 3)
        self.assertEqual(self.wAPI.point_count(100), 3)
        
