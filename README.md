 EventPro - Event Management Web Application

 A modern, full-featured web application built with Python (Flask) and Tailwind CSS to help event planners efficiently manage events, attendees, and revenue.


 Features

   Dashboard: A beautiful overview of total events, attendees, revenue, upcoming events, and recent registrations.
   Event Management (CRUD):
    -   Create, Edit, Update, and Delete events.
    -   Each event includes a title, description, date, location, capacity, and image.
    -   Modern card grid layout with hover animations.
   Attendee Management:
    -   Register new attendees for specific events.
    -   View a list of all attendees for an event.
    -   Prevents duplicate registrations for the same event.
   Advanced Reporting:
    -   A professional reports page with charts and tables.
    -   Visualize revenue by event, and distribution of upcoming vs. past events.
    -   View top events by revenue and event performance (occupancy).
-   QR Code Integration:
    -   Instantly generate and share event links with a QR code.
    -   Automatically send a confirmation email with a unique ticket QR code upon registration.
-   PDF Report Download:
    -   Download a clean, professional PDF summary of all event reports with a single click.
-   CSV Import:
    -   Bulk import multiple events at once by uploading a CSV file.
-   Modern UI/UX:
    -   Clean, responsive design using Tailwind CSS.
    -   Includes a Dark/Light mode theme toggle.

  Tech Stack

-   Backend: Python, Flask, Flask-SQLAlchemy
-   Frontend: HTML5, Tailwind CSS (via CDN), JavaScript
-   Database: SQLite
-   Email & PDF:
    -   `Flask-Mail` for sending confirmation emails via Gmail.
    -   `WeasyPrint` for generating PDF reports from HTML.
-   QR Codes:`qrcode` library.

  Getting Started

Follow these instructions to set up and run the project on your local machine.

 Prerequisites

-   Python 3.10+
-   Git

 Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git)
    cd YOUR-REPOSITORY-NAME
    ```

2.  Create and activate a virtual environment:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  Create a `requirements.txt` file:**
    First, install all the required packages:
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-Mail qrcode Pillow WeasyPrint
    ```
    Then, create the requirements file:
    ```bash
    pip freeze > requirements.txt
    ```
    *(In the future, anyone can just run `pip install -r requirements.txt` to install everything.)*

4.  Set up Email Credentials (for Ticket Confirmation):
    -   This project uses Gmail to send emails. You need a Google App Password.
    -   Go to your Google Account -> Security -> 2-Step Verification (turn it on).
    -   Then go to App passwords, generate a new 16-digit password, and copy it.
    -   In your `app.py` file, find the `Mail Configuration` section and replace the placeholder values:
        ```python
        app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
        app.config['MAIL_PASSWORD'] = 'your-16-digit-app-password'
        ```

5.  Run the application:
    ```bash
    python app.py
    ```
    Open your browser and navigate to `http://127.0.0.1:5000`.

📂 Project Structure

event-management-app/ ├── app.py # Main Flask application ├── database.db # SQLite database ├── README.md # This file ├── requirements.txt # Python packages ├── .gitignore # Files to ignore for Git ├── static/ │ └── js/ │ └── main.js # JavaScript for interactivity └── templates/ ├── layout.html # Base template ├── dashboard.html # Main dashboard page ├── events.html # Events page ├── attendees.html # Attendees page ├── reports.html # Reports dashboard ├── import.html # CSV import page ├── report_pdf.html # Template for PDF download └── ticket_email.html # Template for confirmation email