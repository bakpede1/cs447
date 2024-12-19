# MealMe: Easy Meal Planning

MealMe is a Flask-based meal planner application that allows users to create, bookmark, and manage meal plans. The project integrates a PostgreSQL database, generates meal plan PDFs, and supports image uploads. This project can be deployed and run on [Replit](https://replit.com).

---

## Features
- **User Authentication**: Sign-up, login, and session management.
- **Meal Management**: Users can add custom meals, bookmark meals, and manage weekly meal plans.
- **PDF Export**: Generate and download a detailed weekly meal plan as a PDF.
- **Image Uploads**: Upload custom images for meals.
- **Email Notifications**: Send emails for contact forms and password resets.
- **PostgreSQL Database**: Persistent database integration to store user and meal data.

---

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **PDF Generation**: ReportLab
- **Email Service**: Flask-Mail
- **Frontend**: HTML, CSS
- **Deployment**: Replit (via Reserved VM) --OPTIONAL

---

# How to Use
- **Sign Up:** Create an account and log in.
- **Set Preferences:** Customize dietary preferences and meal settings.
- **Add Meals:** Add custom meals or bookmark from available recipes.
- **Plan Meals:** Use the weekly planner to set meals for each day.
- **Export PDF:** Export your weekly meal plan as a PDF.

## Demo 
[https://go.screenpal.com/u/gvQD/mealme]

##

## Dependencies
- Flask
- Flask-Mail
- Flask-Session
- Psycopg2
- ReportLab
- Requests
- Werkzeug
- Python 3.11+

Install them using:
```bash
pip install flask flask-mail flask-session psycopg2 reportlab requests
```

## To deploy on Replit:

1. Upload the project files to Replit.
2. Ensure requirements.txt includes all dependencies.
3. Run the project using Replit's Run button.

## Setup Instructions

Follow these steps to set up and run the project on Replit or locally.

### 1. Clone the Repository
```bash
git clone https://github.com/bakpede1/cs447.git
```
### 2. Install Dependencies

Use pip to install all required dependencies:
```bash
pip install -r requirements.txt
```
### 3. Environment Setup
Set up a PostgreSQL database and update the database configuration in your project.

- Create a PostgreSQL database.
- Replace database credentials in main.py under the get_db_connection() function:
```bash
conn = psycopg2.connect(
    host="your-db-host",
    database="your-db-name",
    user="your-username",
    password="your-password"
)
```
### 4. Required Files and Directories
Ensure the following structure for the project:
```bash
MealMe/
│
├── static/
│   ├── images/
│   │   └── Mealme-logo.png   # Required for PDF logo
│   └── uploads/              # Stores uploaded meal images
│
├── templates/                # Contains HTML files
├── fonts/                    # Custom fonts for PDF generation
│   ├── Montserrat-Bold.ttf
│   ├── Lexend-Regular.ttf
│   └── Nunito-Light.ttf
│
├── main.py                   # Main application file
├── requirements.txt          # Python dependencies
└── README.md
```

### 5. PostgreSQL Database Setup
Below is the schema used to set up the PostgreSQL database for the Meal Planner application. Each table serves a specific purpose in organizing user and meal data.

#### Users Table
Stores user account details and custom meal preferences.

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    name VARCHAR(80) NOT NULL,
    meal_frequency INT, -- Number of meals per day
    meal_labels VARCHAR[] -- Array of custom meal labels
);
```

#### Preferences Table
Tracks user-specific dietary preferences and restrictions.

```sql
CREATE TABLE preferences (
    preferences_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    dietary_preferences VARCHAR[], -- Array of dietary preferences
    preferred_ingredients VARCHAR[], -- List of preferred ingredients
    allergies_intolerances VARCHAR[], -- List of food intolerances or allergies
    ingredients_to_avoid VARCHAR[] -- List of ingredients to avoid
);
```

#### Meals Table
Stores predefined meal options with tags, ingredients, and instructions.

```sql
CREATE TABLE meals (
    meal_id SERIAL PRIMARY KEY,
    meal_name VARCHAR(120) NOT NULL,
    tags VARCHAR[], -- Dietary tags
    ingredients TEXT NOT NULL,
    instructions TEXT,
    nutrition_info JSON, -- Nutritional information as JSON
    image_url VARCHAR(255) -- URL or file path for the meal image
);
```

#### Custom Meals Table
Enables users to create and save their custom meals.
```sql
CREATE TABLE custom_meals (
    custom_meal_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    meal_name VARCHAR(120) NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT,
    tags VARCHAR[], -- Dietary tags
    nutrition_info JSON, -- Nutritional information as JSON
    image_url VARCHAR(255) -- URL or file path for the custom meal image
);
```

#### Bookmarks Table
Allows users to bookmark predefined meals for quick access.
```sql
CREATE TABLE bookmarks (
    bookmark_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    meal_id INT REFERENCES meals(meal_id) ON DELETE CASCADE -- Links to meals
);
```

#### Meal Planner Table
Stores information about user-specific meal planners.
```sql
CREATE TABLE meal_planners (
    planner_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    creation_date DATE DEFAULT CURRENT_DATE -- Date of creation
);
```

#### Meal Entries Table
Logs the details of each meal entry in a user's planner.
```sql
CREATE TABLE meal_entries (
    meal_entry_id SERIAL PRIMARY KEY,
    planner_id INT NOT NULL REFERENCES meal_planners(planner_id) ON DELETE CASCADE,
    meal_id INT REFERENCES meals(meal_id) ON DELETE CASCADE,
    custom_meal_id INT REFERENCES custom_meals(custom_meal_id) ON DELETE CASCADE,
    day_of_week VARCHAR(10) NOT NULL, -- e.g., "Monday"
    meal_label VARCHAR(50), -- Custom meal label
    specific_time TIME NOT NULL, -- Exact time for the meal
    image_url VARCHAR(255) -- URL for the meal entry image
);
```
### 6. Run the Application
To run the app locally:
```bash
python main.py
```
Open http://localhost:80 in your browser.


## Known Issues
**Dashboard Page:**
- Cards on the dashboard page do not display custom meals. Only meals from the meals table appear correctly.

**PDF Export:**
- Long text for ingredients and instructions sometimes overlaps or gets cut off due to page height constraints. This issue remains unresolved within the current time constraints.

## Important Notes
- **Database:** Ensure the PostgreSQL database is running and accessible.
- **Images:** Images are uploaded to static/uploads/ and can also be fetched via URLs for PDFs.
- **PDF Export:** Fonts like Montserrat, Lexend, and Nunito are required in the fonts/ directory for styling.
- **Emails:** Update MAIL_USERNAME and MAIL_PASSWORD in main.py to configure email services.

## Troubleshooting
- **Database Connection Error:** Verify credentials and ensure the PostgreSQL server is active.
- **Fonts Not Found:** Add missing .ttf font files in the fonts/ directory.
- **Replit Deployment Issue:** Use the Replit shell to install missing dependencies.
  
## Contributors:
Blossom Akpedeye, Kelvin Zheng, DJ Shade

## License
This project is licensed under the MIT License.



