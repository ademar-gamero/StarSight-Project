from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from distance import curr_user

cur_usr = curr_user()
class LocationForm(FlaskForm):
    loc_lat = DecimalField("lat", places=12,rounding=None)
    loc_lon = DecimalField("lng", places=12,rounding=None)
    loc_radius = SelectField('Choose a search radius', choices=[(8.04672,'5 miles'),(16.0934,'10 miles'),(32.1869,'20 miles')], coerce=float)
    submit = SubmitField('Find Stars')
