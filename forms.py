from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from distance import curr_user

cur_usr = curr_user()
class LocationForm(FlaskForm):
    loc_lat = DecimalField("lat", places=12,rounding=None)
    loc_lon = DecimalField("lng", places=12,rounding=None)
    loc_radius = SelectField('Choose a search radius', choices=[(8.04672,'5 miles'),(16.0934,'10 miles'),(32.1869,'20 miles')], coerce=float)
    submit = SubmitField('Find Stars')
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    password = PasswordField('Password', validators=[DataRequired()])

    #confirm_password = PasswordField('Confirm Password',
                                     #validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class AddFriendForm(FlaskForm):
    friend_username = StringField('Friend Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Add Friend')