#imports
from flask import Flask, render_template
from flask import url_for, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

#SETUP
app = Flask(__name__) #flask setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mm.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #sqalchemy setup

'''DATABASE CLASSES GO HERE'''
# User Model
class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    meal_frequency = db.Column(db.Integer, nullable=True)  # Meals per day
    meal_labels = db.Column(db.String(200), nullable=True)  # Labels for meal times

    def __init__(self, user_id, email, password_hash, name, meal_frequency=None, meal_labels=None):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.meal_frequency = meal_frequency
        self.meal_labels = meal_labels

    # Relationships
    preferences = db.relationship('Preference', backref='user', uselist=False, cascade="all, delete-orphan")
    custom_meals = db.relationship('CustomMeal', backref='user', cascade="all, delete-orphan")
    meal_planners = db.relationship('MealPlanner', backref='user', cascade="all, delete-orphan")
    bookmarks = db.relationship('Bookmark', backref='user', cascade="all, delete-orphan")

# Preference Model
class Preference(db.Model):
    __tablename__ = 'preference'

    preference_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    dietary_preferences = db.Column(db.String(120), nullable=True)
    preferred_ingredients = db.Column(db.String(200), nullable=True)
    allergies_intolerances = db.Column(db.String(200), nullable=True)
    ingredients_to_avoid = db.Column(db.String(200), nullable=True)

    def __init__(self, user_id, dietary_preferences=None, preferred_ingredients=None, allergies_intolerances=None, ingredients_to_avoid=None):
        self.user_id = user_id
        self.dietary_preferences = dietary_preferences
        self.preferred_ingredients = preferred_ingredients
        self.allergies_intolerances = allergies_intolerances
        self.ingredients_to_avoid = ingredients_to_avoid

# Meal Model
class Meal(db.Model):
    __tablename__ = 'meal'

    meal_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    tags = db.Column(db.String(100), nullable=True)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    nutrition_info = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)

    def __init__(self, name, ingredients, tags=None, instructions=None, nutrition_info=None, image_url=None):
        self.name = name
        self.ingredients = ingredients
        self.tags = tags
        self.instructions = instructions
        self.nutrition_info = nutrition_info
        self.image_url = image_url

    # Relationships
    meal_entries = db.relationship('MealEntry', backref='meal', cascade="all, delete-orphan")

# CustomMeal Model
class CustomMeal(db.Model):
    __tablename__ = 'custom_meal'

    custom_meal_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(100), nullable=True)
    nutrition_info = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)

    def __init__(self, user_id, name, ingredients, instructions=None, tags=None, nutrition_info=None, image_url=None):
        self.user_id = user_id
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.tags = tags
        self.nutrition_info = nutrition_info
        self.image_url = image_url

        # MealPlanner Model
        class MealPlanner(db.Model):
            __tablename__ = 'meal_planner'

            planner_id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
            creation_date = db.Column(db.DateTime, default=datetime.utcnow)

            def __init__(self, user_id, creation_date=None):
                self.user_id = user_id
                # Only set creation_date if passed, otherwise it uses the default
                if creation_date:
                    self.creation_date = creation_date

        # MealEntry Model
        class MealEntry(db.Model):
            __tablename__ = 'meal_entry'

            entry_id = db.Column(db.Integer, primary_key=True)
            planner_id = db.Column(db.Integer, db.ForeignKey('meal_planner.planner_id'), nullable=False)
            meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=True)
            custom_meal_id = db.Column(db.Integer, db.ForeignKey('custom_meal.custom_meal_id'), nullable=True)
            day_of_week = db.Column(db.String(10), nullable=False)
            meal_label = db.Column(db.String(50), nullable=True)
            specific_time = db.Column(db.Time, nullable=False)
            image_url = db.Column(db.String(200), nullable=True)

            def __init__(self, planner_id, day_of_week, specific_time, meal_id=None, custom_meal_id=None, meal_label=None, image_url=None):
                self.planner_id = planner_id
                self.day_of_week = day_of_week
                self.specific_time = specific_time
                self.meal_id = meal_id
                self.custom_meal_id = custom_meal_id
                self.meal_label = meal_label
                self.image_url = image_url

        # Bookmark Model
        class Bookmark(db.Model):
            __tablename__ = 'bookmark'

            bookmark_id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
            meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=True)
            custom_meal_id = db.Column(db.Integer, db.ForeignKey('custom_meal.custom_meal_id'), nullable=True)

            def __init__(self, user_id, meal_id=None, custom_meal_id=None):
                self.user_id = user_id
                self.meal_id = meal_id
                self.custom_meal_id = custom_meal_id


#TODO: Make preference object when signing up, and how to get data
# from checkboxes to use for db objects/models
@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')

@app.route('/contact', methods=['GET'])
def contact_us_page():
    return render_template('contact_us.html')

@app.route('/create-meal', methods=['GET', 'POST'])
def create_meal_page():
    # access denied if not logged in
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))

    meal_name = request.form.get("meal-name")
    ingredients = request.form.get("ingredients")
    userID = user_id
    if meal_name and ingredients:
        m = CustomMeal(name=meal_name, ingredients=ingredients, user_id=userID)
        db.session.add(m)
        db.session.commit()
        return render_template('create_meal.html')
    else:
        flash('Invalid Input(s)')
    return render_template('create_meal.html')

@app.route('/bookmarks', methods=['GET' , 'POST'])
def bookmarks_page():
    # access denied if not logged in
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))

    
    # no form to get data from in html file
    return render_template('bookmarks.html')

@app.route('/dashboard', methods=['GET'])
def dashboard_page():
    # access denied if not logged in
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/features'. methods=['GET'])
def features_page():
    return render_template('features.html')

@app.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    #need to figure out how to validate credentials
    
    return render_template('login.html')

@app.route('/my-meals', methods=['GET'])
def my_meals_page():
    # access denied if not logged in
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))

    return render_template('my_meals.html')

@app.route('/privacy-policy', methods=['GET'])
def privacy_policy_page():
    return render_template('privacy_policy.html')

@app.route('/profile-settings', methods=['GET'])
def profile_settings_page():
    # access denied if not logged in
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    #need to figure out how to update user settings    
    
    return render_template('profile_settings.html')

@app.route('/recipes', methods=['GET'])
def recipes_page():
    # access denied if not logged in
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    
    return render_template('recipes.html')

@app.route('/terms-of-service', methods=['GET', 'POST'])
def terms_of_service_page():
    return render_template('terms_of_service.html')

@app.route('/signup', methods=['GET'] , 'POST')
def signup_page():
# still need to create preference object
    user_id = str(uuid.uuid4())
    name = request.signup-form.get("name")
    email = request.signup-form.get("email")
    password = request.signup-form.get("password")
    if name and email and request and user_id:
        u = User(user_id=user_id, name=name, email=email, password=password_hash)
        db.session.add(u)
        db.session.commit()
        return render_template('signup.html')
    else:
        flash('Invalid Input(s)')
    return render_template('signup.html')

@app.route('/logout' methods=['GET'])
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create tables (if they dont exist yet)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
