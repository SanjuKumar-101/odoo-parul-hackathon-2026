from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app import mysql
from utils.decorators import login_required
from utils.helpers import generate_share_token, get_trip_status

community_bp = Blueprint('community', __name__)

@community_bp.route('/community')
def index():
    search = request.args.get('q', '').strip()
    region_filter = request.args.get('region', '').strip()
    cur = mysql.connection.cursor()

    sql = """
        SELECT t.*, u.name as author, u.profile_photo as author_photo,
               u.tagline as author_tagline
        FROM trips t JOIN users u ON t.user_id = u.id
        WHERE t.is_public = TRUE
    """
    params = []
    if search:
        sql += " AND (t.name LIKE %s OR t.destination LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    sql += " ORDER BY t.created_at DESC LIMIT 24"

    cur.execute(sql, params)
    trips = cur.fetchall()
    cur.close()
    return render_template('community/index.html', trips=trips, search=search)

@community_bp.route('/community/copy/<int:trip_id>', methods=['POST'])
@login_required
def copy_trip(trip_id):
    cur = mysql.connection.cursor()

    # Get original trip
    cur.execute("SELECT * FROM trips WHERE id = %s AND is_public = TRUE", (trip_id,))
    original = cur.fetchone()
    if not original:
        flash('Trip not found or not public.', 'danger')
        return redirect(url_for('community.index'))

    # Copy trip
    token = generate_share_token()
    status = get_trip_status(str(original['start_date']), str(original['end_date']))
    cur.execute("""
        INSERT INTO trips (user_id, name, destination, start_date, end_date,
                           description, total_budget, status, share_token)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (session['user_id'], f"Copy of {original['name']}", original['destination'],
          original['start_date'], original['end_date'], original['description'],
          original['total_budget'], status, token))
    mysql.connection.commit()
    new_trip_id = cur.lastrowid

    # Copy itinerary days
    cur.execute("SELECT * FROM itinerary_days WHERE trip_id = %s ORDER BY day_number", (trip_id,))
    days = cur.fetchall()
    for day in days:
        cur.execute("""
            INSERT INTO itinerary_days (trip_id, day_number, day_date, city, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_trip_id, day['day_number'], day['day_date'], day['city'], day['notes']))
        mysql.connection.commit()
        new_day_id = cur.lastrowid

        # Copy items for each day
        cur.execute("SELECT * FROM itinerary_items WHERE day_id = %s", (day['id'],))
        items = cur.fetchall()
        for item in items:
            cur.execute("""
                INSERT INTO itinerary_items (day_id, title, description, start_time, end_time, cost, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (new_day_id, item['title'], item['description'],
                  item['start_time'], item['end_time'], item['cost'], item['category']))
        mysql.connection.commit()

    cur.close()
    flash(f'Trip copied successfully! You can now edit it.', 'success')
    return redirect(url_for('trips.view_trip', trip_id=new_trip_id))
