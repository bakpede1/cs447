from flask import Flask, render_template
from flask import url_for, request, flash, redirect, session

app = Flask(__name__)

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

@app.route('/login')
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

if __name__ == '__main__':
    app.run(debug=True)
