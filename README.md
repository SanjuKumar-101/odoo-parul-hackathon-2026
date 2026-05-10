# Traveloop

A full-stack travel planning and itinerary management platform built with Flask and MySQL.

## Tech Stack
- **Backend:** Flask (Python)
- **Database:** MySQL
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript, Chart.js

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure database
Edit `config.py` and set your MySQL credentials:
```python
MYSQL_USER = 'your_user'
MYSQL_PASSWORD = 'your_password'
MYSQL_DB = 'traveloop'
```

### 3. Create the database
```bash
mysql -u root -p < database/schema.sql
```

### 4. Run the app
```bash
python app.py
```

Visit `http://localhost:5000`

## Features
- User authentication (register/login/logout)
- Create and manage multi-city trips
- Day-wise itinerary builder
- Budget & expense tracker with charts
- Packing checklist
- Trip notes / journal
- City & activity search
- Community public trips
- Admin analytics dashboard

## Project Structure
```
traveloop/
├── app.py              # Entry point
├── config.py           # Configuration
├── routes/             # Blueprint route handlers
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS, images
├── database/           # SQL schema & seed data
└── utils/              # Helpers and decorators
```

## Git Workflow
```bash
git init
git checkout -b dev
git add .
git commit -m "feat: initial project scaffold with Flask + MySQL"
```
