#imports
from flask import Flask, render_template
from flask import url_for, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

#SETUP
app = Flask(__name__) #flask setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MealMe.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app) #sqalchemy setup
'''DATABASE CLASSES GO HERE'''

#######################################################################################
# User Model
class User(db.Model):
    __tablename__ = 'user'

    '''ATTRIBUTES'''

    # Relationships
    '''1-TO-1 ETC'''

# Preference Model
class Preference(db.Model):
    __tablename__ = 'preference'


# Meal Model
class Meal(db.Model):
    __tablename__ = 'meal'

    

    # Relationships
    

# CustomMeal Model (User's Custom Meals, MyMeals)
class CustomMeal(db.Model):
    __tablename__ = 'custom_meal'

    

# MealPlanner Model
class MealPlanner(db.Model):
    __tablename__ = 'meal_planner'

    

    # Relationships
    

# MealEntry Model
class MealEntry(db.Model):
    __tablename__ = 'meal_entry'

    

# Bookmark Model
class Bookmark(db.Model):
    __tablename__ = 'bookmark'


#####################################################################



# made routes for each html page (might not need some depending on path)
#TODO: determine which routes need GETs or POSTs (for now)
@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact_us')
def contact_us_page():
    return render_template('contact_us.html')

@app.route('/create_meal')
def create_meal_page():
    return render_template('create_meal.html')

@app.route('/bookmarks')
def bookmarks_page():
    return render_template('bookmarks.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/features')
def features_page():
    return render_template('features.html')

@app.route('/forgot_password')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')

@app.route('/my_meals')
def my_meals_page():
    return render_template('my_meals.html')

@app.route('/privacy_policy')
def privacy_policy_page():
    return render_template('privacy_policy.html')

@app.route('/profile_settings')
def profile_settings_page():
    return render_template('profile_settings.html')

@app.route('/recipes')
def recipes_page():
    return render_template('recipes.html')

@app.route('/terms_of_service')
def terms_of_service_page():
    return render_template('terms_of_service.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create tables (if they dont exist yet)
    db.create_all()
    app.run(host='0.0.0.0', port=5000)
