from flask import Blueprint, render_template, session
from app import mysql
from utils.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Auto-update trip statuses based on today's date
    cur.execute("""
        UPDATE trips SET status = CASE
            WHEN CURDATE() < start_date THEN 'upcoming'
            WHEN CURDATE() > end_date THEN 'completed'
            ELSE 'ongoing'
        END
        WHERE user_id = %s
    """, (user_id,))
    mysql.connection.commit()

    # Recent trips
    cur.execute("""
        SELECT * FROM trips WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 5
    """, (user_id,))
    recent_trips = cur.fetchall()

    # Trip counts
    cur.execute("SELECT COUNT(*) as total FROM trips WHERE user_id = %s", (user_id,))
    total_trips = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as cnt FROM trips WHERE user_id = %s AND status='upcoming'", (user_id,))
    upcoming = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM trips WHERE user_id = %s AND status='completed'", (user_id,))
    completed = cur.fetchone()['cnt']

    # Popular cities
    cur.execute("SELECT * FROM cities ORDER BY popularity DESC LIMIT 6")
    popular_cities = cur.fetchall()

    cur.close()
    return render_template('dashboard/index.html',
                           recent_trips=recent_trips,
                           total_trips=total_trips,
                           upcoming=upcoming,
                           completed=completed,
                           popular_cities=popular_cities)
