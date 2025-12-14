# Employee Attendance System
## Privacy Note

**This is a demonstration version.** Real employee names, emails, and credentials have been replaced with examples for privacy and security. The actual production system runs on a private company network with real employee data.

When deploying, make sure to:
- Replace all example employee data with your actual employees
- Create a `.env` file with secure credentials (never commit this!)
- Change the default admin password
- Configure your timezone and office hours

A Flask-based attendance tracking system with email verification, timezone support, and admin dashboard. **Built from scratch by a 12-year-old developer without AI assistance.**

## Features

- **Email Verification**: 5-digit codes sent to employee emails for sign-in/sign-out
- **Auto-Detection**: Automatically detects system username and maps to employee
- **Timezone Support**: Handles night shift (6 PM - 3 AM EST)
- **Late Tracking**: Calculates and records late arrivals
- **Admin Dashboard**: View attendance overview, late employees, and detailed records
- **Weekly Database**: Organizes attendance data by week folders
- **Shared Accounts**: Supports multiple employees using same workstation

## Tech Stack

- **Backend**: Flask, SQLite3
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Features**: Email verification, session management, timezone handling (pytz)

## About This Project

This entire system was built by hand without AI code generation. Every feature - from the email verification flow to the timezone calculations to the admin dashboard - was coded manually while learning Flask and web development.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/TextModeKid/attendance-system.git
cd attendance-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
SECRET_KEY=your_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password_here
```

4. Run the application:
```bash
python main.py
```

5. Access at `http://localhost:5000`

## How It Works

1. Employee visits homepage
2. System auto-detects their username or they select manually
3. Employee requests sign-in/sign-out
4. 5-digit verification code generated and "sent" to their email
5. Employee enters code to confirm action
6. Attendance recorded in daily SQLite database
7. Admin can view all records in dashboard

## Configuration

### Employee Setup
Edit `EMPLOYEES` and `EMPLOYEE_EMAILS` in `main.py`

### System Username Mapping
Map Windows usernames to employees in `SYSTEM_USERNAME_MAP`

### Office Hours
Adjust `OFFICE_START` and `OFFICE_END` for your timezone

## Database Structure

Organized by week folders for easy management:
```
db/
├── week_2025_45/
│   ├── attendance_2025-11-16.db
│   └── attendance_2025-11-17.db
└── week_2025_46/
    └── ...
```

⚠️ **Important**: This repository contains example data only. Before deploying:

### 1. Update Employee Information
Edit `main.py` and replace example employees with your actual staff:
```python
EMPLOYEES = [
    "Your Employee 1", "Your Employee 2", # etc...
]

EMPLOYEE_EMAILS = {
    "Your Employee 1": "employee1@yourcompany.com",
    "Your Employee 2": "employee2@yourcompany.com",
    # Add all your employees
}
```

### 2. Create `.env` File
Create a `.env` file in the root directory (never commit this file):
```bash
SECRET_KEY=your_random_secret_key_here
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. System Username Mapping
Map your Windows/Linux usernames to employees:
```python
SYSTEM_USERNAME_MAP = {
    "your_pc_username": {"name": "Employee Name", "email": "email@company.com"},
    "shared_pc": {
        "users": ["Employee 1", "Employee 2"]
    }
}
```

### 4. Configure Office Hours
Adjust timezone and shift times in `main.py`:
```python
TIMEZONE = pytz.timezone("Your/Timezone")  # e.g., "America/New_York"
OFFICE_START = datetime.strptime("18:00", "%H:%M").time()
OFFICE_END = datetime.strptime("03:00", "%H:%M").time()
```

## What I Learned

- Flask routing and session management
- SQLite database operations
- Timezone handling with pytz
- Form validation and security
- JavaScript fetch API
- Dynamic HTML/CSS design

## Future Plans

- [ ] Integrate real email service (SendGrid/AWS SES)
- [ ] Export attendance to Excel/CSV
- [ ] Mobile-responsive design
- [ ] Multi-language support
- [ ] Edit/delete attendance records from admin panel

## License

MIT License

## Author

**TerminalProdigy** - 12-year-old developer | Self-taught Python, HTML, CSS | Arch & Gentoo Linux user | Learning by building real-world applications
