from flask import Blueprint, render_template
from app import mysql
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_required
def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) as total FROM users")
    total_users = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM trips")
    total_trips = cur.fetchone()['total']

    cur.execute("SELECT SUM(total_budget) as total FROM trips")
    total_budget = cur.fetchone()['total'] or 0

    cur.execute("""
        SELECT status, COUNT(*) as cnt FROM trips GROUP BY status
    """)
    trip_by_status = cur.fetchall()

    cur.execute("""
        SELECT c.name, COUNT(t.id) as trip_count
        FROM trips t JOIN cities c ON t.destination = c.name
        GROUP BY c.name ORDER BY trip_count DESC LIMIT 5
    """)
    top_cities = cur.fetchall()

    cur.execute("""
        SELECT u.name, u.email, COUNT(t.id) as trip_count
        FROM users u LEFT JOIN trips t ON u.id = t.user_id
        GROUP BY u.id ORDER BY trip_count DESC LIMIT 10
    """)
    users = cur.fetchall()

    cur.execute("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as cnt
        FROM trips GROUP BY month ORDER BY month DESC LIMIT 6
    """)
    trips_by_month = cur.fetchall()

    cur.close()
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_trips=total_trips,
                           total_budget=total_budget,
                           trip_by_status=trip_by_status,
                           top_cities=top_cities,
                           users=users,
                           trips_by_month=trips_by_month)
