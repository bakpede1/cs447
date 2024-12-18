#imports
import secrets
import string
import json
import requests
import platform
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, send_file
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from reportlab.lib import colors


from flask_session import Session


#set system time
time_format = "%-I:%M %p" if platform.system() != "Windows" else "%I:%M %p"

#SETUP
app = Flask(__name__)  #flask setup
app.secret_key = 'aWds123@$%i(03nf'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)

#MAIL CONFIG
# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mealme.assist@gmail.com'
app.config['MAIL_PASSWORD'] = 'gbsr xfht awhw lbmz'

mail = Mail(app)

#for report lab export pdf fucntion
# Register custom fonts
pdfmetrics.registerFont(TTFont('Montserrat', 'fonts/Montserrat-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Lexend', 'fonts/Lexend-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Nunito', 'fonts/Nunito-Light.ttf'))

def get_db_connection():
    """ Function to get a database connection """
    conn = psycopg2.connect(
        host="",
        database="",
        user='',
        password='')
    return conn

def generate_temp_password(length=12):
    """
    Generates a secure random password of the given length.

    Parameters:
    - length (int): Length of the generated password. Default is 12.

    Returns:
    - str: A secure, random password.
    """
    # Define the character set for the password
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_+="

    # Generate a password using secure random choices
    temp_password = ''.join(secrets.choice(characters) for _ in range(length))

    return temp_password

def download_image(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return ImageReader(BytesIO(response.content))
    except Exception as e:
        print(f"Failed to download image: {url}. Error: {e}")
    return None
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    

# GUIDE: This is how to open a cursor to perform database operations
#cur = conn.cursor()

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        dietary_preferences = request.form.getlist('dietary-preferences')
        dietary_restrictions = request.form.getlist('dietary-restrictions')
        meal_frequency = request.form.get('meal-frequency')

        # Backend validation
        if not (name and email and password and meal_frequency):
            flash('All fields are required.', 'error')
            return redirect('/signup')

        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Generate a hashed password
            hashed_password = generate_password_hash(password)

            # Insert user into the `users` table
            cur.execute(
                """
                INSERT INTO users (email, password, name, meal_frequency)
                VALUES (%s, %s, %s, %s) RETURNING user_id
            """, (email, hashed_password, name, meal_frequency))
            user_id = cur.fetchone()[0]

            # Insert preferences into the `preferences` table
            cur.execute(
                """
                INSERT INTO preferences (user_id, dietary_preferences, ingredients_to_avoid)
                VALUES (%s, %s, %s)
            """, (user_id, dietary_preferences, dietary_restrictions))

            conn.commit()

            # Set the session
            session['user_id'] = user_id
            session['name'] = name
            flash('Signup successful! Welcome to MealMe.', 'success')
            return redirect('/login')

        except Exception as e:
            # Rollback in case of an error
            conn.rollback()
            print(f"Error during signup: {e}")
            flash('An error occurred during signup. Please try again.',
                  'error')
            return redirect('/signup')

        finally:
            if conn:
                conn.close()

    return render_template('signup.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect('/login')

@app.route('/contact', methods=['GET'])
def contact_us_page():

    return render_template('contact_us.html')

# Route to handle form submission for contact us page
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic validation
        if not name or not email or not subject or not message:
            flash("All fields are required.", "error")
            return redirect('/contact')

        try:
            # Prepare the email
            msg = Message(subject=f"Contact Form Submission: {subject}",
                          sender=email,
                          recipients=['mealme.assist@gmail.com'])
            msg.body = f"""
            New Contact Form Submission:

            Name: {name}
            Email: {email}
            Subject: {subject}
            Message: {message}
            """
            mail.send(msg)

            # Send a success message
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            print(f"Error sending email: {e}")
            flash("There was an error submitting the form. Please try again.",
                  "error")

    return redirect('/contact')  # Redirect to clear the form

@app.route('/my-meals/create', methods=['GET', 'POST'])
def create_meal_page():
    # Access denied if not logged in
    if 'name' not in session:
        flash('Please log in first', 'error')
        return redirect('/login')

    meal_id = request.args.get('meal_id')  # To check if editing
    meal_data = {}

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Preload existing meal data for editing
        if meal_id:
            cursor.execute("SELECT * FROM custom_meals WHERE custom_meal_id = %s", (meal_id,))
            meal_data = cursor.fetchone()

        if request.method == 'POST':
            # Required form fields
            meal_name = request.form.get("meal-name")
            ingredients = request.form.get("ingredients")
            description = request.form.get("description") or None
            instructions = request.form.get("instructions") or None
            nutrition_info = request.form.get("nutrition-info") or None
            tags = request.form.getlist("tags") + request.form.getlist("restrictions")

            # Image file handling
            photo = request.files.get("photo")
            image_url = meal_data.get("image_url") if meal_data else None

            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo_path = app.config['UPLOAD_FOLDER'] + '/' + filename
                photo.save(photo_path)
                image_url = f"/static/uploads/{filename}"

            # Validate required fields
            if not meal_name or not ingredients:
                flash('Meal Name and Ingredients are required.', 'error')
                return redirect(request.url)

            # Fetch user_id correctly (Fix single-item tuple)
            cursor.execute("SELECT user_id FROM users WHERE name = %s", (session['name'],))  # Trailing comma is needed
            user = cursor.fetchone()
            if not user:
                flash('User not found. Please log in again.', 'error')
                return redirect('/login')
            user_id = user['user_id']

            # Insert or Update Logic
            if meal_id:
                # Update existing meal
                cursor.execute("""
                    UPDATE custom_meals 
                    SET meal_name = %s, ingredients = %s, instructions = %s, tags = %s, nutrition_info = %s, image_url = %s
                    WHERE custom_meal_id = %s AND user_id = %s
                """, (meal_name, ingredients, instructions, tags or '[]', json.dumps(nutrition_info) if nutrition_info else '{}', image_url, meal_id, user_id))
                flash('Meal updated successfully!', 'success')
            else:
                # Insert new meal
                cursor.execute("""
                    INSERT INTO custom_meals (user_id, meal_name, ingredients, instructions, tags, nutrition_info, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, meal_name, ingredients, instructions, tags or '[]', json.dumps(nutrition_info) if nutrition_info else '{}', image_url))
                flash('Meal created successfully!', 'success')

            conn.commit()
            return redirect('/my-meals')

    except Exception as e:
        print(f"Error creating meal: {e}")
        flash('An error occurred. Please try again.', 'error')
    finally:
        cursor.close()
        conn.close()

    return render_template('create_meal.html', meal_data=meal_data)

# Delete Meal
@app.route('/my-meals/delete/<int:meal_id>', methods=['POST'])
def delete_meal(meal_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM custom_meals WHERE custom_meal_id = %s AND user_id = %s",
                       (meal_id, session['user_id']))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Could not delete meal"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/bookmarks', methods=['GET', 'POST'])
def bookmarks_page():
    if 'user_id' not in session:
        flash('Please log in first', 'error')
        return redirect('/login')

    user_id = session['user_id']  # Retrieve user ID from session
    conn = get_db_connection()
    cursor = conn.cursor()
    meals = []

    try:
        # Default query to fetch bookmarked meals
        query = """
            SELECT m.meal_id, m.meal_name, m.image_url, m.ingredients, m.instructions, m.nutrition_info, m.tags
            FROM meals m
            JOIN bookmarks b ON m.meal_id = b.meal_id
            WHERE b.user_id = %s
        """
        params = [user_id]

        # Sorting functionality
        sort_option = request.form.get('sort-options')
        if sort_option == 'A-Z':
            query += " ORDER BY m.meal_name ASC"
        elif sort_option == 'Z-A':
            query += " ORDER BY m.meal_name DESC"

        # Filtering functionality
        selected_diets = request.form.getlist('diet')
        selected_restrictions = request.form.getlist('restriction')

        # Apply filters dynamically
        if selected_diets:
            query += " AND (" + " OR ".join(" %s = ANY(m.tags)" for _ in selected_diets) + ")"
            params.extend(selected_diets)

        if selected_restrictions:
            query += " AND NOT (" + " OR ".join(" %s = ANY(m.tags)" for _ in selected_restrictions) + ")"
            params.extend(selected_restrictions)

        # Clear all bookmarks if button pressed
        if 'clear-bookmarks' in request.form:
            cursor.execute("DELETE FROM bookmarks WHERE user_id = %s", (user_id,))
            conn.commit()
            flash('All bookmarks cleared successfully!', 'success')
            return redirect('/bookmarks')

        # Execute the query to fetch meals
        cursor.execute(query, tuple(params))
        meals = cursor.fetchall()

        # Convert to list of dictionaries
        meals = [
            {
                'meal_id': row[0],
                'meal_name': row[1],
                'image_url': row[2],
                'ingredients': row[3],
                'instructions': row[4],
                'nutrition_info': row[5],
                'tags': row[6]
            }
            for row in meals
        ]

    except Exception as e:
        print(f"Error fetching bookmarks: {e}")
        flash("Error fetching bookmarks. Please try again later.", "error")
    finally:
        cursor.close()
        conn.close()

    return render_template('bookmarks.html', meals=meals)

@app.route('/clear-bookmarks', methods=['POST'])
def clear_bookmarks():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    user_id = session['user_id']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete all bookmarks for the logged-in user
        cursor.execute("DELETE FROM bookmarks WHERE user_id = %s", (user_id,))
        conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error clearing bookmarks: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard_page():
    # Access denied if not logged in
    if 'name' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    meal_preferences = {}
    user_meals = []
    current_meals = {}
    weekly_overview = None

    try:
        # Step 1: Fetch User ID
        cursor.execute("SELECT user_id FROM users WHERE name = %s", (session['name'],))
        user_row = cursor.fetchone()
        if not user_row:
            flash('User not found. Please log in again.', 'error')
            return redirect('/login')

        user_id = user_row['user_id']

        # Step 2: Ensure Planner Exists
        cursor.execute("SELECT planner_id FROM meal_planners WHERE user_id = %s", (user_id,))
        planner_row = cursor.fetchone()

        if not planner_row:
            cursor.execute("""
                INSERT INTO meal_planners (user_id, creation_date)
                VALUES (%s, CURRENT_DATE)
                RETURNING planner_id
            """, (user_id,))
            planner_id = cursor.fetchone()['planner_id']
            conn.commit()
            flash('Default meal planner created!', 'success')
        else:
            planner_id = planner_row['planner_id']

        #Fetch Weekly Overview Data
        cursor.execute("""
            SELECT day_of_week, meal_label, specific_time, meals.meal_name
            FROM meal_entries
            LEFT JOIN meals ON meal_entries.meal_id = meals.meal_id
            WHERE planner_id = %s
        """, (planner_id,))
        weekly_overview = cursor.fetchall()

        
        # Step 3: Fetch User Meal Preferences
        cursor.execute("SELECT meal_labels, meal_times, meal_frequency FROM users WHERE user_id = %s", (user_id,))
        meal_preferences = cursor.fetchone()

        if not meal_preferences:
            flash('No meal preferences found. Set your preferences first.', 'error')
            return redirect('/profile-settings')

        # Convert meal_times to 12-hour format
        meal_preferences['meal_times'] = [
            datetime.strptime(time, "%H:%M").strftime("%I:%M %p").lstrip('0')
            for time in meal_preferences['meal_times']
        ]

        # Step 4: Fetch User Meals (Bookmarked and Custom Meals)
        cursor.execute("""
            SELECT meals.meal_id, meals.meal_name 
            FROM bookmarks 
            JOIN meals ON bookmarks.meal_id = meals.meal_id
            WHERE bookmarks.user_id = %s

            UNION ALL

            SELECT custom_meals.custom_meal_id AS meal_id, custom_meals.meal_name 
            FROM custom_meals
            WHERE custom_meals.user_id = %s
        """, (user_id, user_id))

        user_meals = cursor.fetchall()

        # Step 5: Fetch Current Meals in Planner for Prefill
        cursor.execute("""
            SELECT day_of_week, meal_label, meal_id, custom_meal_id 
            FROM meal_entries
            WHERE planner_id = %s
        """, (planner_id,))
        current_entries = cursor.fetchall()

        for entry in current_entries:
            current_meals.setdefault(entry['day_of_week'], {})[entry['meal_label']] = entry['meal_id'] or entry['custom_meal_id']

        # Step 6: Handle POST Request (Update Meal Entries)
        if request.method == 'POST':
            # Clear existing planner entries before inserting new ones
            cursor.execute("DELETE FROM meal_entries WHERE planner_id = %s", (planner_id,))

            # Insert updated meals
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                for idx, label in enumerate(meal_preferences['meal_labels']):
                    meal_id = request.form.get(f"{day.lower()}-{label.lower()}")
                    if meal_id:
                        cursor.execute("""
                            INSERT INTO meal_entries (planner_id, day_of_week, meal_label, specific_time, meal_id)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (planner_id, day, label, meal_preferences['meal_times'][idx], meal_id))
            conn.commit()
            flash('Meal plan updated successfully!', 'success')

            # **Re-fetch Current Meals to Update Template Immediately**
            cursor.execute("""
                SELECT day_of_week, meal_label, meal_id, custom_meal_id 
                FROM meal_entries
                WHERE planner_id = %s
            """, (planner_id,))
            current_entries = cursor.fetchall()

            current_meals = {}
            for entry in current_entries:
                current_meals.setdefault(entry['day_of_week'], {})[entry['meal_label']] = entry['meal_id'] or entry['custom_meal_id']
                
    except Exception as e:
        print(f"Error in dashboard: {e}")
        flash('Something went wrong. Please try again.', 'error')
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'dashboard.html',
        meal_preferences=meal_preferences,
        user_meals=user_meals,
        current_meals=current_meals, 
        weekly_overview=weekly_overview
    )

@app.route('/export-pdf', methods=['GET'])
def export_pdf():
    if 'name' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Get the plan name (user input from frontend)
        plan_name = request.args.get('plan_name', 'Weekly Meal Overview')

        # Fetch user ID and planner
        cursor.execute("SELECT user_id FROM users WHERE name = %s", (session['name'],))
        user_id = cursor.fetchone()['user_id']

        cursor.execute("""
            SELECT 
                meal_entries.day_of_week, 
                meal_entries.meal_label, 
                meal_entries.specific_time, 
                meals.meal_name AS meal_name, 
                custom_meals.meal_name AS custom_meal_name,
                meals.ingredients AS meal_ingredients, 
                custom_meals.ingredients AS custom_meal_ingredients,
                meals.instructions AS meal_instructions,
                custom_meals.instructions AS custom_meal_instructions,
                meals.image_url AS meal_image_url,
                custom_meals.image_url AS custom_meal_image_url
            FROM meal_entries
            LEFT JOIN meals ON meal_entries.meal_id = meals.meal_id
            LEFT JOIN custom_meals ON meal_entries.custom_meal_id = custom_meals.custom_meal_id
            WHERE planner_id = (SELECT planner_id FROM meal_planners WHERE user_id = %s)
        """, (user_id,))

        meal_entries = cursor.fetchall()

        # Format the data
        formatted_entries = []
        for entry in meal_entries:
            formatted_entries.append({
                'day_of_week': entry['day_of_week'],
                'meal_label': entry['meal_label'],
                # Properly format time without lstrip
                'specific_time': entry['specific_time'].strftime(time_format).lstrip('0'),
                'meal_name': entry['meal_name'] or entry['custom_meal_name'],
                'ingredients': entry['meal_ingredients'] or entry['custom_meal_ingredients'],
                'instructions': entry['meal_instructions'] or entry['custom_meal_instructions'],
                'image_url': entry['meal_image_url'] or entry['custom_meal_image_url']
            })
            
        # Organize meals by day
        meals_by_day = {}
        for entry in formatted_entries:
            day = entry['day_of_week']
            meals_by_day.setdefault(day, []).append(entry)

        # Generate PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Page 1: Weekly Overview
        logo_path = "static/images/Mealme-logo.png"  # Place logo in a static folder
        pdf.drawImage(logo_path, 50, height - 70, width=1.5*inch, height=1.5*inch, preserveAspectRatio=False)
        pdf.setFont("Montserrat", 18)
        pdf.setFillColor(colors.HexColor('#2C3E50'))
        pdf.drawString(180, height - 50, plan_name.upper())
        pdf.line(50, height - 60, width - 50, height - 60)

        y = height - 100
        for day, meals in meals_by_day.items():
            pdf.setFont("Montserrat", 14)
            pdf.setFillColor(colors.HexColor('#FF6384'))
            pdf.drawString(50, y, f"{day}:")

            for meal in meals:
                meal_name = meal['meal_name'] or meal['custom_meal_name']
                meal_time = meal['specific_time']


                pdf.setFont("Nunito", 10)
                pdf.setFillColor(colors.HexColor('#5A5A5A'))
                pdf.drawString(70, y - 15, f"{meal['meal_label']} - {meal_time} - {meal_name}")
                y -= 25

                if y < 50:
                    pdf.showPage()
                    y = height - 50

        pdf.showPage()

        # Pages 2–8: Detailed Meals
        for day, meals in meals_by_day.items():
            pdf.setFont("Montserrat", 18)
            pdf.setFillColor(colors.HexColor('#FF6384'))
            pdf.drawString(50, height - 50, f"{day} Meals")

            y = height - 100

            for meal in meals:
                # Meal Details
                pdf.setFont("Montserrat", 12)
                pdf.setFillColor(colors.HexColor('#4A4A4A'))
                meal_time = meal['specific_time']
                pdf.drawString(50, y, f"{meal['meal_label']} - {meal_time}")

                pdf.setFont("Lexend", 10)
                meal_name = meal['meal_name'] or meal['custom_meal_name']
                ingredients = meal['ingredients'] or meal['custom_ingredients']
                instructions = meal['instructions'] or meal['custom_instructions']
                image_url = meal['image_url'] or meal['custom_image_url']

                pdf.setFillColor(colors.black)
                pdf.drawString(70, y - 15, f"Meal: {meal_name}")
                pdf.drawString(70, y - 30, f"Ingredients: {ingredients}")
                pdf.drawString(70, y - 45, f"Instructions: {instructions}")

                # Draw Image if available
                if image_url:
                    try:
                        image = ImageReader(image_url)
                        pdf.drawImage(image, 400, y - 50, width=1.5*inch, height=1.5*inch, preserveAspectRatio=True)
                    except Exception as e:
                        print(f"Image error: {e}")

                y -= 90
                if y < 100:
                    pdf.showPage()
                    y = height - 50

            pdf.showPage()

        # Save PDF and return
        pdf.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="weekly_meal_plan.pdf")

    except Exception as e:
        print(f"Error exporting PDF: {e}")
        flash('An error occurred while generating the PDF.', 'error')
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate input
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('login_page'))
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Query user by email
            cursor.execute(
                "SELECT user_id, name, password FROM users WHERE email = %s",
                (email, ))
            user = cursor.fetchone()

            if user is None:
                flash('No account found with this email.', 'error')
                return redirect(url_for('login_page'))

            user_id, name, hashed_password = user

            # Validate password
            if not check_password_hash(hashed_password, password):
                flash('Incorrect password.', 'error')
                return redirect(url_for('login_page'))

            # Store user info in session
            session['user_id'] = user_id
            session['name'] = name
            flash('Login successful!', 'success')
            return redirect(url_for('profile_settings_page'))

        except Exception as e:
            print(f"Error during login: {e}")
            flash('An error occurred. Please try again later.', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/my-meals', methods=['GET'])
def my_meals_page():
    # access denied if not logged in
    if 'user_id' not in session:
        flash('Please log in first', 'error')
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM custom_meals WHERE user_id = %s", (session['user_id'],))
        meals = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        meals = []
    finally:
        cursor.close()
        conn.close()

    return render_template('my_meals.html', meals=meals)

@app.route('/recipes', methods=['GET', 'POST'])
def recipes_page():
    # Ensure the user is logged in
    if 'name' not in session:
        flash('Please log in first', 'error')
        return redirect('/login')

    user_id = session.get('user_id')  # Assuming `user_id` is stored in the session after login
    conn = get_db_connection()
    cursor = conn.cursor()
    meals = []

    # Base query for fetching meals with a LEFT JOIN to check bookmarks
    query = """
        SELECT 
            m.meal_id, 
            m.meal_name, 
            m.tags, 
            m.ingredients, 
            m.instructions, 
            m.nutrition_info, 
            m.image_url,
            CASE WHEN b.meal_id IS NOT NULL THEN TRUE ELSE FALSE END AS bookmarked
        FROM meals m
        LEFT JOIN bookmarks b ON m.meal_id = b.meal_id AND b.user_id = %s
        WHERE 1=1
    """
    params = [user_id]

    try:
        if request.method == 'POST':
            # Collect filters from the form
            dietary_preferences = request.form.getlist('dietary-preferences')
            dietary_restrictions = request.form.getlist('dietary-restrictions')

            # Add dietary preferences filter
            if dietary_preferences:
                query += " AND (" + " OR ".join(" %s = ANY(m.tags) " for _ in dietary_preferences) + ")"
                params.extend(dietary_preferences)

            # Add dietary restrictions filter (to exclude)
            if dietary_restrictions:
                query += " AND NOT (" + " OR ".join(" %s = ANY(m.tags) " for _ in dietary_restrictions) + ")"
                params.extend(dietary_restrictions)

        # Execute the query
        cursor.execute(query, tuple(params))
        meals = cursor.fetchall()

        # Convert the result into a list of dictionaries
        meals = [
            {
                'meal_id': row[0],
                'meal_name': row[1],
                'tags': row[2],
                'ingredients': row[3],
                'instructions': row[4],
                'nutrition_info': row[5],
                'image_url': row[6],
                'bookmarked': row[7]  # True or False
            }
            for row in meals
        ]

    except Exception as e:
        print(f"Error fetching recipes: {e}")
        flash("Error fetching recipes. Please try again later.", "error")
    finally:
        cursor.close()
        conn.close()

    # Pass recipes to the template
    return render_template('recipes.html', meals=meals)

@app.route('/toggle-bookmark', methods=['POST'])
def toggle_bookmark():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    meal_id = data.get('meal_id')
    action = data.get('action')  # 'add' or 'remove'
    user_id = session['user_id']

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if action == 'add':
            # Check if already bookmarked
            cursor.execute("SELECT * FROM bookmarks WHERE user_id = %s AND meal_id = %s", (user_id, meal_id))
            if not cursor.fetchone():
                # Add bookmark
                cursor.execute("INSERT INTO bookmarks (user_id, meal_id) VALUES (%s, %s)", (user_id, meal_id))
        elif action == 'remove':
            # Remove bookmark
            cursor.execute("DELETE FROM bookmarks WHERE user_id = %s AND meal_id = %s", (user_id, meal_id))

        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password_page():
    #connect to db
    conn = get_db_connection()

    #look for email in db
    if request.method == 'POST':
        email = request.form['email']
        email = str(email)
        try:
            # Check if email exists in the database
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE email = %s",
                               (email, ))
                user = cursor.fetchone()

                if user:
                    # Generate a temporary password
                    temp_password = generate_temp_password()

                    # Hash the temporary password
                    hashed_password = generate_password_hash(temp_password)

                    # Update the database with the temporary password
                    cursor.execute(
                        "UPDATE users SET password = %s WHERE email = %s",
                        (hashed_password, email))
                    conn.commit()

                    # Send an email with the temporary password
                    msg = Message(subject="Password Reset for MealMe",
                                  sender=app.config['MAIL_USERNAME'],
                                  recipients=[email])
                    msg.body = f'''Hello,\n\nYour temporary password is: {temp_password}\n\nPlease log in and change your password as soon as possible.\n\nBest regards,\nMealMe Support Team'''
                    mail.send(msg)

                    flash(
                        "A reset link has been sent to your email. Please check your inbox.",
                        "success")
                else:
                    flash("This email is not registered in our system.",
                          "error")

        except Exception as e:
            print(e)
            flash(
                "An error occurred while processing your request. Please try again later.",
                "error")

    return render_template('forgot_password.html')

@app.route('/features', methods=['GET'])
def features_page():
    return render_template('features.html')

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')

@app.route('/profile-settings', methods=['GET', 'POST'])
def profile_settings_page():
    # Ensure the user is logged in
    if 'name' not in session:
        flash('Please log in first', 'error')
        return redirect('/login')

    user_id = session.get(
        'user_id')  # Assuming `user_id` is stored in the session after login
    conn = get_db_connection()
    cursor = conn.cursor()

    meal_frequency = None
    meal_labels = []
    meal_times = []
    preferences = None
    if request.method == 'GET':
        # Fetch meal frequency, labels, and times
        cursor.execute(
            """
            SELECT meal_frequency, meal_labels, meal_times
            FROM users WHERE user_id = %s
        """, (user_id,))
        result =  cursor.fetchone()
        if result:
            meal_frequency, meal_labels, meal_times = result

        # Fetch preferences
        cursor.execute(
            """
            SELECT dietary_preferences, ingredients_to_avoid
            FROM preferences WHERE user_id = %s
        """, (user_id,))
        preferences = cursor.fetchone()

        cursor.close()
        conn.close()

    return render_template(
        'profile_settings.html',
        meal_frequency=meal_frequency if meal_frequency else 3,
        meal_labels=meal_labels,
        meal_times=meal_times,
        preferences=preferences
    )

@app.route('/update-preferences', methods=['POST'])
def update_preferences():
    if 'user_id' not in session:
        flash("You must be logged in to update preferences.", "error")
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()

    # Get form inputs
    dietary_preferences = request.form.getlist(
        'dietary_preferences')  # List of selected preferences
    dietary_restrictions = request.form.getlist(
        'ingredients_to_avoid')  # List of selected restrictions

    # For dietary_preferences
    dietary_preferences = '{' + ','.join(f'"{item}"'
                                         for item in dietary_preferences) + '}'

    # For dietary_restrictions
    dietary_restrictions = '{' + ','.join(
        f'"{item}"' for item in dietary_restrictions) + '}'

    try:
        # Fetch current preferences
        cur.execute(
            """
            SELECT dietary_preferences, ingredients_to_avoid
            FROM preferences
            WHERE user_id = %s
        """, (user_id, ))
        current_preferences = cur.fetchone()

        # Retain existing values if no new data is provided
        if not dietary_preferences:
            dietary_preferences = current_preferences[
                0] if current_preferences[0] else []
        if not dietary_restrictions:
            dietary_restrictions = current_preferences[
                1] if current_preferences[1] else []

        # Update preferences in the database
        cur.execute(
            """
            UPDATE preferences
            SET dietary_preferences = %s,
                ingredients_to_avoid = %s 
            WHERE user_id = %s
        """, (dietary_preferences, dietary_restrictions, user_id))
        conn.commit()
        flash("Preferences updated successfully!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error updating preferences: {e}", "error")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('profile_settings_page'))

@app.route('/update-meal-settings', methods=['POST'])
def update_meal_settings():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to update meal settings.", "error")
        return redirect(url_for('login_page'))

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Get the number of meals
        meals_per_day = request.form.get('meal_frequency')
        
        # Collect meal labels and times
        meal_labels = []
        meal_times = []

        for i in range(1, int(meals_per_day) + 1):
            label = request.form.get(f'meal_name_{i}')
            time = request.form.get(f'meal_time_{i}')
            if label and time:
                meal_labels.append(label)
                meal_times.append(time)

        # Update meal settings in the database
        cur.execute(
            """
            UPDATE users
            SET meal_frequency = %s,
                meal_labels = %s,
                meal_times = %s
            WHERE user_id = %s
        """, (meals_per_day, meal_labels, meal_times, user_id))
        conn.commit()
        flash("Meal settings updated successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error updating meal settings: {e}", "error")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('profile_settings_page'))

@app.route('/update-password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        flash("You must be logged in to update your password.", "error")
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    
    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "error")
        return redirect(url_for('profile_settings_page'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Verify current password
        cur.execute("SELECT password FROM users WHERE user_id = %s",
                    (user_id, ))
        stored_password = cur.fetchone()
        if not stored_password or not check_password_hash(
                stored_password[0], current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for('profile_settings_page'))

        # Update new password
        hashed_password = generate_password_hash(new_password)
        cur.execute(
            """
            UPDATE users
            SET password = %s
            WHERE user_id = %s
        """, (hashed_password, user_id))
        conn.commit()
        flash("Password updated successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error updating password: {e}", "error")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('profile_settings_page'))

@app.route('/privacy-policy', methods=['GET'])
def privacy_policy_page():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service', methods=['GET', 'POST'])
def terms_of_service_page():
    return render_template('terms_of_service.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
