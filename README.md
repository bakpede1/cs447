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

### 5. Run the Application
To run the app locally:
```bash
python main.py
```
Open http://localhost:80 in your browser.

## To deploy on Replit:

1. Upload the project files to Replit.
2. Ensure requirements.txt includes all dependencies.
3. Run the project using Replit's Run button.

## Dependencies
Flask
Flask-Mail
Flask-Session
Psycopg2
ReportLab
Requests
Werkzeug
Python 3.11+

Install them using:
```bash
pip install flask flask-mail flask-session psycopg2 reportlab requests
```

# How to Use
- **Sign Up:** Create an account and log in.
- **Set Preferences:** Customize dietary preferences and meal settings.
- **Add Meals:** Add custom meals or bookmark from available recipes.
- **Plan Meals:** Use the weekly planner to set meals for each day.
- **Export PDF:** Export your weekly meal plan as a PDF.

## Known Issues
**Dashboard Page:**

- Cards on the dashboard page do not display custom meals. Only meals from the meals table appear correctly.
PDF Export:

**Text Overlap:** 
- Long text for ingredients and instructions sometimes overlaps or gets cut off due to page height constraints. This issue remains unresolved

## Important Notes
**Database:** Ensure the PostgreSQL database is running and accessible.
**Images:** Images are uploaded to static/uploads/ and can also be fetched via URLs for PDFs.
**PDF Export:** Fonts like Montserrat, Lexend, and Nunito are required in the fonts/ directory for styling.
**Emails:** Update MAIL_USERNAME and MAIL_PASSWORD in main.py to configure email services.

## Troubleshooting
**Database Connection Error:** Verify credentials and ensure the PostgreSQL server is active.
**Fonts Not Found:** Add missing .ttf font files in the fonts/ directory.
**Replit Deployment Issue:** Use the Replit shell to install missing dependencies.


## License
This project is licensed under the MIT License.



