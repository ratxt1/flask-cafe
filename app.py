"""Flask App for Flask Cafe."""


from flask import Flask, render_template, request, flash, jsonify
from flask import redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Cafe, City, User, UserLikesCafe
from forms import AddOrEditCafeForm, SignupForm, LoginForm, ProfileEditForm
from sqlalchemy.exc import IntegrityError




from secrets import FLASK_SECRET_KEY


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///flaskcafe'
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)


#######################################
# auth & auth routes

CURR_USER_KEY = "user_id"
NOT_LOGGED_IN_MSG = "You are not logged in."


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]




#######################################
# homepage

@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# cafes


@app.route('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
    )

@app.route('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
    )

@app.route('/cafes/add', methods=['GET', 'POST'])
def add_cafe_form():
    """ GET: show add cafe form, POST: adds cafe to database"""
    if not g.user or not g.user.admin:
        return 'not authorized', 401

    form = AddOrEditCafeForm()
    form.city_code.choices = db.session.query(City.code, City.name).all()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        url = form.url.data
        address = form.address.data
        city_code = form.city_code.data
        image_url = form.image_url.data

        cafe = Cafe(
            name=name,
            description=description,
            url=url,
            address=address,
            city_code=city_code,
            image_url=image_url
        )
        
        db.session.add(cafe)
        db.session.commit()
        cafe.save_map()


        flash(f'{name} added')
        return redirect(f'/cafes/{cafe.id}')
    else:
        return render_template('cafe/add-form.html', form=form)


@app.route('/cafes/<cafe_id>/edit', methods=['GET', 'POST'])
def edit_cafe_form(cafe_id):
    """ GET: show cafe edit form, POST: update cafe details """
    if not g.user or not g.user.admin:
        return 'not authorized', 401

    cafe = Cafe.query.get_or_404(cafe_id)

    form = AddOrEditCafeForm(obj=cafe)
    form.city_code.choices = db.session.query(City.code, City.name).all()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        url = form.url.data
        address = form.address.data
        city_code = form.city_code.data
        image_url = form.image_url.data

        cafe.name = name
        cafe.description = description
        cafe.url = url
        cafe.address = address
        cafe.city_code = city_code
        cafe.image_url = image_url


        db.session.commit()
        cafe.save_map()

        flash(f'{name} edited')
        return redirect(f'/cafes/{cafe.id}')
    else:
        return render_template('cafe/edit-form.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup_user():
    """ Registers user """

    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        description = form.description.data
        email = form.email.data
        password = form.password.data
        image_url = form.image_url.data

        user = User.register(
            username=username,
            first_name=first_name,
            last_name=last_name,
            description=description,
            email=email,
            password=password,
            image_url=image_url
        )

        db.session.add(user)
        db.session.commit()

        do_login(user)

        flash('You are signed up and logged in.')

        return redirect('/cafes')
    else:
        return render_template('auth/signup-form.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ Logs in user """
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            do_login(user)
            flash(f'Hello, {username}!')
            return redirect("/cafes")

        else:
            form.username.errors = ["Invalid credentials"]

    return render_template('auth/login-form.html', form=form)

@app.route('/logout', methods=['POST'])
def logout_user():
    """ Logs user out """
    do_logout()

    flash('You should have successfully logged out.')
    return redirect('/cafes')

@app.route('/profile')
def show_profile():
    """ show user profile """
    if not g.user:
        flash(NOT_LOGGED_IN_MSG)
        return redirect('/login')
    else:
        return render_template('profile/detail.html')


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """ GET: show profile edit form, POST: updates user profile """
    if not g.user:
        flash(NOT_LOGGED_IN_MSG)
        return redirect('/login')

    form = ProfileEditForm(obj=g.user)

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        description = form.description.data
        email = form.email.data
        image_url = form.image_url.data

        g.user.first_name=first_name
        g.user.last_name=last_name
        g.user.description=description
        g.user.email=email
        g.user.image_url=image_url

        db.session.commit()

        flash('Profile edited.')
        return redirect('/profile')

    else:
        return render_template('profile/edit-form.html', form=form)

@app.route('/api/likes')
def check_if_user_likes_cafe():
    """ Check if user has liked cafe

        Returns JSON: {error}
    """
    if not g.user:
        return jsonify(error="Not logged in")
    
    cafe_id = request.args['cafe_id']
    
    return jsonify(likes=g.user.has_liked(cafe_id))

@app.route('/api/like', methods=['POST'])
def like_cafe():
    """ Likes a post, stores the 'like' in database

        Returns JSON: {error}
    """

    if not g.user:
        return jsonify(error="Not logged in")

    cafe_id = request.json['cafe_id']

    g.user.liked_cafes.append(Cafe.query.get_or_404(cafe_id))

    db.session.commit()

    return jsonify(liked=cafe_id)

@app.route('/api/unlike', methods=['POST'])
def unlike_cafe():
    """ Unlikes a post, delete the 'like' from database

        Returns JSON: {error}
    """

    if not g.user:
        return jsonify(error="Not logged in")

    cafe_id = request.json['cafe_id']

    g.user.liked_cafes.remove(Cafe.query.get_or_404(cafe_id))

    db.session.commit()

    return jsonify(unliked=cafe_id)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404