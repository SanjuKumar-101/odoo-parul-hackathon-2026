# Traveloop

Traveloop is a full-stack travel planning and itinerary management web application built for the Odoo X Parul University hackathon qualification round.

It helps users create multi-day trips, manage itinerary activities, track expenses, prepare packing checklists, write trip notes, discover destinations, and share public itineraries.

## Tech Stack

- Backend: Flask
- Database: MySQL
- Frontend: HTML, CSS, Bootstrap 5, JavaScript
- Charts: Chart.js
- Database driver: Flask-MySQLdb with PyMySQL compatibility

Traveloop does not depend on third-party travel APIs. City and activity data are stored in MySQL seed tables so the application remains dynamic and database-backed.

## Core Features

- User registration, login, logout, and session-based access control
- Trip creation, editing, deletion, status tracking, and public sharing
- City discovery with MySQL-backed search and filters
- Activity discovery by city and category
- City autocomplete backed by internal Flask JSON endpoints
- Day-wise itinerary builder
- Activity cost planning
- Budget dashboard with expense tracking and category charts
- INR-based currency conversion display for budget readability
- Packing checklist with packed/unpacked state
- Trip notes and journal entries
- Community page for public itineraries
- Admin analytics dashboard and city/user/trip management
- Responsive UI with a polished travel-product visual system
- User-friendly flash messages and custom error pages
- Destination-locked itinerary days to prevent unrelated city entries
- Emergency contact numbers for supported destination cities

## Project Structure

```text
traveloop/
  app.py                  # Flask application factory and blueprint registration
  config.py               # Environment-based configuration
  wsgi.py                 # Deployment entry point
  requirements.txt        # Python dependencies
  database/schema.sql     # MySQL schema and seed data
  routes/                 # Feature-based Flask blueprints
  templates/              # Jinja templates
  static/css/main.css     # Global UI system and responsive styling
  static/js/              # App JavaScript and internal API-powered autocomplete
  static/images/          # Destination and profile images
```

## Database Design

The app uses normalized MySQL tables with foreign keys:

- `users`
- `cities`
- `activities`
- `trips`
- `itinerary_days`
- `itinerary_items`
- `expenses`
- `packing_items`
- `trip_notes`

The schema also includes a `budgets` table for category budget expansion, while the current UI primarily tracks actual spending through `expenses`.

## Internal Backend APIs

Traveloop includes lightweight internal JSON endpoints:

- `GET /api/cities?q=<query>` for city autocomplete
- `GET /api/cities/validate?name=<city>` for typed city validation

These endpoints read from MySQL and do not call third-party services.

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and update the values:

```bash
SECRET_KEY=replace-with-a-long-random-secret
FLASK_DEBUG=1
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=traveloop
```

Do not commit `.env`. It is already ignored by `.gitignore`.

### 4. Create and seed the MySQL database

Run the SQL file in MySQL:

```bash
mysql -u root -p < database/schema.sql
```

For an existing Traveloop database, run the latest migration instead of recreating the database:

```bash
mysql -u root -p traveloop < database/migrations/2026_05_10_final_features.sql
```

This creates the `traveloop` database and inserts seed cities and activities.

### 5. Run the app locally

```bash
python app.py
```

Or:

```bash
python -m flask --app app:create_app run
```

Open:

```text
http://127.0.0.1:5000
```

## Deployment Notes

Use environment variables in production. At minimum, set:

- `SECRET_KEY`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DB`
- `FLASK_DEBUG=0`

The WSGI entry point is:

```text
wsgi:app
```

For a Linux host, a typical production command is:

```bash
gunicorn wsgi:app
```

If your host does not provide Gunicorn automatically, add it to the deployment environment or use the platform's recommended WSGI server.

## Judge-Focused Highlights

- Modular Flask Blueprint architecture by feature area
- MySQL-backed dynamic data instead of static JSON
- Parameterized SQL queries for safer database access
- Normalized database schema with foreign keys and cascading deletes
- Internal backend API endpoints for autocomplete
- Clear validation and user-facing flash messages
- Custom 404, 413, and 500 error pages
- Responsive, polished UI with consistent navigation and visual hierarchy
- Public itinerary sharing and community trip copying
- Admin analytics with Chart.js visualizations

## Version Control Checklist

Before final submission:

```bash
git status
git add .
git commit -m "Prepared Traveloop for final deployment readiness"
git push
```

Make sure `.env` is not committed.
