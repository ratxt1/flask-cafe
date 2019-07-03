"""Forms for Flask Cafe."""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, BooleanField, SelectField, TextField, PasswordField
from wtforms.validators import InputRequired, Optional, URL, Email, Length, EqualTo


class AddOrEditCafeForm(FlaskForm):
    """ Form for adding or editing cafe. """

    name = StringField(
        "Name",
        validators=[InputRequired()]
    )

    description = TextField(
        "Description",
        validators=[InputRequired()]
    )

    url = StringField(
        "URL",
        validators=[InputRequired(), URL()]
    )

    address = StringField(
        "Address",
        validators=[InputRequired()]
    )

    city_code = SelectField(
        "City",

    )

    image_url = StringField(
        "Image",
        validators=[InputRequired(), URL()]
    )
    
class SignupForm(FlaskForm):
    """ Form for user sign up """

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )

    first_name = StringField(
        "First name",
        validators=[InputRequired()]
    )

    last_name = StringField(
        "Last name",
        validators=[InputRequired()]
    )

    description = TextField(
        "Description"
    )

    email = StringField(
        "Email",
        validators=[Email()]
    )

    password = PasswordField(
        'Password', 
        [InputRequired(), 
        Length(min=6)]
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()]
    )

class LoginForm(FlaskForm):
    """ Form for user login"""

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )

class ProfileEditForm(FlaskForm):
    """ Form for editing user """

    first_name = StringField(
        "First name",
        validators=[InputRequired()]
    )

    last_name = StringField(
        "Last name",
        validators=[InputRequired()]
    )

    description = TextField(
        "Description"
    )

    email = StringField(
        "Email",
        validators=[Email()]
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()]
    )