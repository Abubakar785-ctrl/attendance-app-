#########imports########
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import pytz
from pathlib import Path
import os
from dotenv import load_dotenv
import random
import string
import socket
import getpass
import smtplib
from email.message import EmailMessage
# For CSV report generation
import csv
from io import StringIO
from flask import Response
#########imports########


load_dotenv()

# --- CONFIGURATION ---
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

TIMEZONE = pytz.timezone("America/New_York")
OFFICE_START = datetime.strptime("18:00", "%H:%M").time()  # 6:00 PM
OFFICE_END = datetime.strptime("03:00", "%H:%M").time()    # 3:00 AM

def is_late(current_time):
    """Check if employee is late. Handles night shift (6 PM - 3 AM)."""
    # If current time is >= 6 PM (18:00), they are late if > 18:00
    # If current time is < 3 AM (03:00), they are on time (within night shift)
    if current_time >= OFFICE_START:
        # Evening/night: any time after 6 PM is late
        return current_time > OFFICE_START
    else:
        # Early morning: before 3 AM is on time
        return False

def calculate_late_minutes(current_time):
    """Calculate how many minutes late the employee is."""
    if not is_late(current_time):
        return 0
    
    # Calculate minutes difference between current time and office start
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
    start_seconds = OFFICE_START.hour * 3600 + OFFICE_START.minute * 60
    
    late_seconds = current_seconds - start_seconds
    late_minutes = int(late_seconds // 60)
    return late_minutes

def generate_verification_code():
    """Generate a random 5-digit code."""
    return ''.join(random.choices(string.digits, k=5))




def send_verification_code(employee_name, code, action, email_override=None):
    """Send verification code to employee email using SMTP."""
    email = email_override or EMPLOYEE_EMAILS.get(employee_name)
    if not email:
        return False

    # Create email
    msg = EmailMessage()
    msg["Subject"] = f"{action.upper()} Verification Code"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = email
    msg.set_content(f"Hello {employee_name},\n\nYour {action} verification code is: {code}\n\nThank you.")

    try:
        with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
            server.starttls()  # secure the connection
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.send_message(msg)
        print(f"[EMAIL] Sent to {email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email to {email}: {e}")
        return False


# admin ony these are allowed ot get in to the admin dashboard
admin_emplyees = ["nauman", "saleem", "zanrbs", "abubakar"]
# now create a function to only allowed admin to go to the admin dashboard

def is_admin(employee_name):
    return employee_name in admin_emplyees

# List of employees - update these with actual employee names

EMPLOYEES = [
    "nauman", "Employee 2", "Employee 3", "Employee 4",
    "Employee 5", "Employee 6", "Employee 7", "Employee 8",
    "Employee 9", "Employee 10", "Employee 11", "Employee 12", "Employee 13", "abubakar"
]

# Employee emails - update these with actual emails
EMPLOYEE_EMAILS = {
    "nauman": "naumantariq482@gmail.com",
    "Employee 2": "employee2@example.com",
    "Employee 3": "employee3@example.com",
    "Employee 4": "employee4@example.com",
    "Employee 5": "employee5@example.com",
    "Employee 6": "employee6@example.com",
    "Employee 7": "employee7@example.com",
    "Employee 8": "employee8@example.com",
    "Employee 9": "employee9@example.com",
    "Employee 10": "employee10@example.com",
    "Emplsoyee 11": "employee11@example.com",
}

# Map Windows usernames to employee names and their emails
SYSTEM_USERNAME_MAP = {
    "user1": {"name": "Employee 1", "email": "employee1@example.com"},
    "shared_pc": {
        "users": ["Employee 2", "Employee 3", "Employee 4"]
    },
    "user2": {"name": "Employee 5", "email": "employee5@example.com"},
    "user3": {"name": "Employee 1", "email": "employee1@example.com"}
}

# Create a lower-cased lookup map so username matching is case-insensitive
NORMALIZED_SYSTEM_USERNAME_MAP = {k.lower(): v for k, v in SYSTEM_USERNAME_MAP.items()}



# Store verification codes temporarily: {employee_name: code}
VERIFICATION_CODES = {}

ADMIN_CREDENTIALS = {
    "username": os.getenv("ADMIN_USERNAME", "admin"),
    "password": os.getenv("ADMIN_PASSWORD", "admin@123")
}

# --- DATABASE SETUP ---
BASE_DB_FOLDER = Path("db")


# make a function to download the monthly report of all employees attendance in csv format
def download_monthly_report(year, month):
    """Download monthly attendance report as CSV."""
    # Prepare CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Date", "Sign In", "Sign Out", "Status", "Late By", "Worked Hours"])

    # Iterate through all week folders of the month
    for week_folder in BASE_DB_FOLDER.glob("week_*"):
        for db_file in week_folder.glob("attendance_*.db"):
            db_date_str = db_file.stem.split("_")[1]
            db_date = datetime.strptime(db_date_str, "%Y-%m-%d")
            if db_date.year == year and db_date.month == month:
                conn = sqlite3.connect(db_file)
                c = conn.cursor()
                c.execute("SELECT name, date, sign_in, sign_out, status, late_by, worked_hours FROM attendance")
                rows = c.fetchall()
                for row in rows:
                    writer.writerow(row)
                conn.close()

    output.seek(0)
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment;filename=attendance_report_{year}_{month}.csv"})


def get_weekly_attendance_csv():
    """Get current week's attendance report as CSV."""
    # Prepare CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Date", "Sign In", "Sign Out", "Status", "Late By", "Worked Hours"])

    # Get current week folder
    week_folder = get_week_folder()
    
    # Iterate through all database files in current week folder
    for db_file in sorted(week_folder.glob("attendance_*.db")):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("SELECT name, date, sign_in, sign_out, status, late_by, worked_hours FROM attendance ORDER BY name")
        rows = c.fetchall()
        for row in rows:
            writer.writerow(row)
        conn.close()

    output.seek(0)
    
    # Generate filename with current week info
    now = datetime.now(TIMEZONE)
    year, week, _ = now.isocalendar()
    filename = f"attendance_week_{year}_w{week}.csv"
    
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment;filename={filename}"})


def get_week_folder():
    """Return the current week folder path (e.g. db/week_2025_45)."""
    now = datetime.now(TIMEZONE)
    year, week, _ = now.isocalendar()
    week_folder = BASE_DB_FOLDER / f"week_{year}_{week}"
    week_folder.mkdir(parents=True, exist_ok=True)
    return week_folder

def get_daily_db_path():
    """Return today’s attendance.db path (inside week folder)."""
    today_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    db_path = get_week_folder() / f"attendance_{today_str}.db"
    if not db_path.exists():
        create_database(db_path)
    return db_path

def create_database(db_path):
    """Create attendance table if DB doesn't exist."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            sign_in TEXT,
            sign_out TEXT,
            status TEXT,
            late_by TEXT,
            worked_hours TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(get_daily_db_path())


# --- ROUTES ---

@app.route("/")
def index():
    return render_template("index.html", employees=EMPLOYEES, employee_emails=EMPLOYEE_EMAILS)


@app.route("/get-system-email", methods=["GET"])
def get_system_email():
    """Get the email associated with the current system user."""
    try:
        username = getpass.getuser()  # Keep original case
        username_lc = username.lower()
        print(f"[DEBUG] System username detected: {username}")

        # Case-insensitive lookup
        user_data = NORMALIZED_SYSTEM_USERNAME_MAP.get(username_lc)
        if user_data:
            print(f"[DEBUG] Found mapping for {username_lc}: {user_data}")

            # If it has "users" key, it's a shared account
            if "users" in user_data:
                # Shared account with locked email
                email = user_data.get("email")
                users_list = user_data["users"]
                print(f"[DEBUG] Shared account with email: {email}, users: {users_list}")
                return {
                    "email": email,  # Locked email for this account
                    "multiple": True,
                    "users": users_list
                }, 200

            # Single user account
            if "name" in user_data:
                return {
                    "email": user_data["email"],
                    "name": user_data["name"]
                }, 200

        # Not found: provide a friendly fallback so the front-end can present manual selection
        print(f"[DEBUG] Username '{username}' not found in mapping (checked '{username_lc}')")
        return {
            "email": None,
            "multiple": False,
            "employees": EMPLOYEES,
            "message": f"Employee not found for username: {username}. Please select manually."
        }, 200
    except Exception as e:
        print(f"[DEBUG] Error: {str(e)}")
        return {"error": str(e)}, 400




@app.route("/request-code", methods=["POST"])
def request_code():
    """Request a verification code for sign-in or sign-out."""
    email = request.form.get("email")
    action = request.form.get("action")  # "sign_in" or "sign_out"
    selected_name = request.form.get("selected_name")  # optional: selected employee name
    
    # Determine which employee this is: prefer explicit selected_name (useful for shared accounts)
    employee_name = None
    if selected_name:
        employee_name = selected_name
    else:
        for name, emp_email in EMPLOYEE_EMAILS.items():
            if emp_email == email:
                employee_name = name
                break

    if not employee_name:
        return {"status": "error", "message": "Employee not found in our system"}, 400
    
    if action not in ["sign_in", "sign_out"]:
        return {"status": "error", "message": "Invalid action"}, 400
    
    # Generate and store verification code (keyed by employee name so selected_name is tracked)
    code = generate_verification_code()
    VERIFICATION_CODES[employee_name] = {"code": code, "action": action, "timestamp": datetime.now(TIMEZONE)}

    # Send code to the provided email (account email for shared accounts)
    send_verification_code(employee_name, code, action, email_override=email)
    
    return {"status": "success", "message": f"Verification code sent to {email}"}, 200


@app.route("/verify-and-submit", methods=["POST"])
def verify_and_submit():
    """Verify code and process attendance."""
    email = request.form.get("email")
    code = request.form.get("code")
    action = request.form.get("action")
    selected_name = request.form.get("selected_name")  # optional: preferred name (for shared accounts or manual selection)
    
    # Determine which employee this is: prefer explicit selected_name
    employee_name = None
    if selected_name:
        employee_name = selected_name
    else:
        for name, emp_email in EMPLOYEE_EMAILS.items():
            if emp_email == email:
                employee_name = name
                break

    if not employee_name:
        return "Employee not found in our system", 400
    
    # Check if verification code exists and matches
    if employee_name not in VERIFICATION_CODES:
        return "No verification code requested. Request one first.", 400
    
    stored_code_data = VERIFICATION_CODES[employee_name]
    if stored_code_data["code"] != code:
        return "Invalid verification code", 400
    
    if stored_code_data["action"] != action:
        return "Action mismatch. Request a new code.", 400
    
    # Check if code is not older than 5 minutes
    code_age = (datetime.now(TIMEZONE) - stored_code_data["timestamp"]).total_seconds()
    if code_age > 300:  # 5 minutes
        del VERIFICATION_CODES[employee_name]
        return "Verification code expired. Request a new one.", 400
    
    # Code is valid, process attendance
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now(TIMEZONE)
    today_str = now.strftime("%Y-%m-%d")
    
    c.execute("SELECT * FROM attendance WHERE name=? AND date=?", (employee_name, today_str))
    record = c.fetchone()
    
    if action == "sign_in":
        if record and record[3]:
            conn.close()
            del VERIFICATION_CODES[employee_name]
            return "Already signed in", 400
        
        sign_in_time = now.strftime("%H:%M:%S")
        late_by = "-"
        
        # Check if employee is late
        if is_late(now.time()):
            late_minutes = calculate_late_minutes(now.time())
            late_by = f"{late_minutes} min late"
        
        if record:
            c.execute("UPDATE attendance SET sign_in=?, status=?, late_by=? WHERE name=? AND date=?",
                      (sign_in_time, "Present", late_by, employee_name, today_str))
        else:
            c.execute("INSERT INTO attendance (name, date, sign_in, status, late_by) VALUES (?, ?, ?, ?, ?)",
                      (employee_name, today_str, sign_in_time, "Present", late_by))
    
    elif action == "sign_out":
        if not record or not record[3]:
            conn.close()
            del VERIFICATION_CODES[employee_name]
            return "Invalid action (sign in first)", 400
        if record[4]:
            conn.close()
            del VERIFICATION_CODES[employee_name]
            return "Already signed out", 400
        
        sign_out_time = now.strftime("%H:%M:%S")
        sign_in_time = datetime.strptime(record[3], "%H:%M:%S").replace(tzinfo=None)
        worked_delta = now.replace(tzinfo=None) - sign_in_time
        hours, minutes = divmod(worked_delta.seconds // 60, 60)
        worked_hours = f"{hours}h {minutes}m"
        c.execute("UPDATE attendance SET sign_out=?, worked_hours=? WHERE name=? AND date=?",
                  (sign_out_time, worked_hours, employee_name, today_str))
    
    conn.commit()
    conn.close()
    
    # Clean up verification code
    del VERIFICATION_CODES[employee_name]
    
    return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form["username"] == ADMIN_CREDENTIALS["username"]
                and request.form["password"] == ADMIN_CREDENTIALS["password"]):
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"
    return render_template("admin.html")


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    db_path = get_daily_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name, date, sign_in, sign_out, status, late_by, worked_hours FROM attendance")
    data = c.fetchall()
    conn.close()

    all_employees = EMPLOYEES
    signed_in = [d[0] for d in data if d[2] and not d[3]]
    signed_out = [d[0] for d in data if d[3]]
    late = [d[0] for d in data if d[5] != "-" and d[5] is not None]
    absent = [e for e in all_employees if e not in signed_in and e not in signed_out]

    today_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    return render_template("dashboard.html",
                           today=today_str,
                           all_employees=all_employees,
                           signed_in=signed_in,
                           signed_out=signed_out,
                           late=late,
                           absent=absent,
                           records=data,
                           office_time="6:00 PM – 3:00 AM (America/New_York)")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/download-weekly-report")
def download_weekly_report():
    """Download current week's attendance as CSV."""
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    return get_weekly_attendance_csv()


@app.route("/download-monthly-report/<int:year>/<int:month>")
def download_monthly_report_route(year, month):
    """Download monthly attendance report as CSV."""
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    return download_monthly_report(year, month)

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=5000)

