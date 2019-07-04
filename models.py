"""Data models for Flask Cafe"""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from secrets import MAPQUEST_API_KEY as API_KEY
import os
import requests


bcrypt = Bcrypt()
db = SQLAlchemy()


class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default="/static/images/default-cafe.jpg",
    )

    city = db.relationship("City", backref='cafes')
    liking_users = db.relationship('User', secondary="users_like_cafes")

    
    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'


    def get_map_url(self):
        """Get MapQuest URL for a static map for this location."""
        address = self.address
        city = self.city.name
        state = self.city.state

        base = f"https://www.mapquestapi.com/staticmap/v5/map?key={API_KEY}"
        where = f"{address},{city},{state}"
        return f"{base}&center={where}&size=@2x&zoom=15&locations={where}"


    def save_map(self):
        """Get static map and save in static/maps directory of this app."""
        id = self.id
        address = self.address
        city = self.city.name
        state = self.city.state

        path = os.path.abspath(os.path.dirname(__file__))
        url = self.get_map_url()
        response = requests.get(url)
        with open(f'{path}/static/images/maps/{id}.jpeg', "wb") as f:
            f.write(response.content)


class User(db.Model):
    """Users for cafes."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.Text,
        unique=True,
        nullable=False,
    )

    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    email = db.Column(
        db.Text,
        unique=True,
        nullable=False,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
    )

    hashed_password = db.Column(
        db.Text,
        nullable=False,
    )

    liked_cafes = db.relationship('Cafe', secondary="users_like_cafes")

    @classmethod
    def register(
        cls, 
        username, 
        password, 
        email, 
        first_name, 
        last_name, 
        description, 
        image_url="",
        admin=False
        ):
        """ Hashes user password, creates and returns a new user """
        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode('utf8')

        return cls(
            username=username, 
            hashed_password=hashed_utf8, 
            admin=admin, 
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            description=description, 
            image_url=image_url
            )


        # u = cls(
        #     username=username, 
        #     hashed_password=hashed_utf8, 
        #     admin=admin, 
        #     email=email, 
        #     first_name=first_name, 
        #     last_name=last_name, 
        #     description=description, 
        #     image_url=image_url
        #     )

        # db.session.add(u)


        # try:
        #      db.session.flush()     # the integrity 
        # except IE:
        #      raise UsernameTakenError()
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.hashed_password, pwd):
            # return user instance
            return u
        else:
            return False
    
    def get_full_name(self):
        """ Returns first_name and last_name for user """
        return self.first_name + " " + self.last_name

    def has_liked(self, cafe_id):
        return Cafe.query.get(cafe_id) in self.liked_cafes


class UserLikesCafe(db.Model):
    """ Middle table for Cafe and User defining what cafes a user likes """

    __tablename__ = 'users_like_cafes'

    cafe_id = db.Column(
        db.Integer,
        db.ForeignKey("cafes.id"),
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True,
    )

    def __repr__(self):
        return f"<UserLikesCafe {self.cafe_id}  {self.user_id}>"


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

