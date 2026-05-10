# Traveloop

Traveloop is a full-stack travel planning and itinerary management web application built for the **Odoo X Parul University Hackathon 2026** qualification round.

It helps users plan and manage trips from one centralized platform by allowing them to create trips, build day-wise itineraries, track expenses, prepare packing checklists, write trip notes, discover destinations, view emergency contacts, and share public itineraries.

---

## Live Demo

**Live App:**  
https://odoo-parul-hackathon-2026.vercel.app/login

**GitHub Repository:**  
https://github.com/SanjuKumar-101/odoo-parul-hackathon-2026

---

## Problem Statement

Travel planning is often scattered across multiple tools such as notes apps, spreadsheets, messaging apps, maps, and travel websites. Users may plan destinations in one place, budgets somewhere else, activities in another app, and packing lists separately.

Traveloop solves this problem by providing a structured, database-driven travel planning platform where users can manage the complete travel workflow from trip creation to itinerary planning, expense tracking, checklist management, notes, and public sharing.

---

## Key Objectives

- Provide a clean and responsive travel planning interface.
- Store and manage real user data dynamically using MySQL.
- Avoid dependency on third-party travel APIs.
- Support complete trip management from planning to sharing.
- Demonstrate scalable backend structure using Flask Blueprints.
- Provide a polished user experience suitable for real-world use.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask |
| Database | MySQL |
| Cloud Database | Aiven MySQL |
| Deployment | Vercel |
| Frontend | HTML, CSS, Bootstrap 5, JavaScript |
| Charts | Chart.js |
| Database Driver | PyMySQL |
| Version Control | Git and GitHub |

Traveloop does not rely on third-party travel APIs. City, activity, itinerary, budget, checklist, emergency contact, and trip data are managed through MySQL, making the application dynamic and database-backed.

---

## Core Features

### User Management

- User registration
- User login and logout
- Session-based access control
- Profile management
- Admin access control

### Trip Management

- Create trips
- View trips
- Edit trips
- Delete trips
- Track trip status
- Share trips publicly
- View public/shared itineraries

### Itinerary Planning

- Day-wise itinerary builder
- Destination-locked itinerary planning
- Activity selection by destination
- Activity cost planning
- Structured itinerary view

### City and Activity Discovery

- MySQL-backed city search
- Activity search by city and category
- City autocomplete using internal Flask JSON endpoints
- Destination images for improved user experience

### Budget and Expense Tracking

- Add and manage trip expenses
- Category-wise expense tracking
- Budget dashboard
- Chart.js-based visual summaries
- INR-based currency display for better readability

### Packing Checklist

- Add packing items
- Mark items as packed or unpacked
- Delete checklist items
- Organize travel preparation

### Trip Notes

- Add travel notes
- Store trip-related reminders
- Maintain journal-style trip information

### Community and Sharing

- Public trip feed
- Shared itinerary view
- Community trip discovery
- Public read-only trip plans

### Admin Dashboard

- Admin-only access
- User management
- Trip management
- City management
- Analytics dashboard
- Chart-based data visualization

### Safety Feature

- Emergency contact numbers for supported destination cities
- Travel safety information available through destination data

---

## Project Structure

```text
traveloop/
├── app.py                  # Flask application factory and blueprint registration
├── config.py               # Environment-based configuration
├── wsgi.py                 # WSGI deployment entry point
├── vercel_app.py           # Vercel serverless entry point
├── vercel.json             # Vercel deployment configuration
├── requirements.txt        # Python dependencies
├── database/
│   ├── schema.sql          # MySQL schema and seed data
│   └── migrations/         # Database migration files
├── routes/                 # Feature-based Flask blueprints
├── templates/              # Jinja2 HTML templates
├── static/
│   ├── css/main.css        # Global UI system and responsive styling
│   ├── js/                 # JavaScript and autocomplete logic
│   └── images/             # Destination and profile images
└── utils/                  # Helper functions and decorators
