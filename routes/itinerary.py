from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import mysql
from utils.decorators import login_required
from datetime import datetime, timedelta

itinerary_bp = Blueprint('itinerary', __name__)

def _get_trip_or_404(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    cur.close()
    return trip

@itinerary_bp.route('/trips/<int:trip_id>/itinerary')
@login_required
def builder(trip_id):
    trip = _get_trip_or_404(trip_id)
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM itinerary_days WHERE trip_id = %s ORDER BY day_number", (trip_id,))
    days = [dict(row) for row in cur.fetchall()]
    for day in days:
        cur.execute("SELECT * FROM itinerary_items WHERE day_id = %s ORDER BY start_time", (day['id'],))
        day['items'] = cur.fetchall()
    cur.close()

    return render_template('itinerary/builder.html', trip=trip, days=days)

@itinerary_bp.route('/trips/<int:trip_id>/itinerary/add_day', methods=['POST'])
@login_required
def add_day(trip_id):
    trip = _get_trip_or_404(trip_id)
    if not trip:
        return jsonify({'error': 'Not found'}), 404

    city = request.form.get('city', '').strip()
    day_date = request.form.get('day_date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not day_date:
        flash('Day date is required.', 'danger')
        return redirect(url_for('itinerary.builder', trip_id=trip_id))

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM itinerary_days WHERE trip_id = %s", (trip_id,))
    count = cur.fetchone()['cnt']
    day_number = count + 1

    cur.execute("""
        INSERT INTO itinerary_days (trip_id, day_number, day_date, city, notes)
        VALUES (%s, %s, %s, %s, %s)
    """, (trip_id, day_number, day_date, city, notes))
    mysql.connection.commit()
    cur.close()

    flash('Day added.', 'success')
    return redirect(url_for('itinerary.builder', trip_id=trip_id))

@itinerary_bp.route('/itinerary/day/<int:day_id>/add_item', methods=['POST'])
@login_required
def add_item(day_id):
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    start_time = request.form.get('start_time', '') or None
    end_time = request.form.get('end_time', '') or None
    cost = request.form.get('cost', '0').strip()
    category = request.form.get('category', 'general').strip()

    if not title:
        flash('Activity title is required.', 'danger')
        return redirect(request.referrer)

    try:
        cost = float(cost)
        if cost < 0:
            raise ValueError
    except ValueError:
        flash('Invalid cost value.', 'danger')
        return redirect(request.referrer)

    cur = mysql.connection.cursor()
    cur.execute("SELECT trip_id FROM itinerary_days WHERE id = %s", (day_id,))
    day = cur.fetchone()
    if not day:
        flash('Day not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    cur.execute("""
        INSERT INTO itinerary_items (day_id, title, description, start_time, end_time, cost, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (day_id, title, description, start_time, end_time, cost, category))
    mysql.connection.commit()
    trip_id = day['trip_id']
    cur.close()

    flash('Activity added.', 'success')
    return redirect(url_for('itinerary.builder', trip_id=trip_id))

@itinerary_bp.route('/itinerary/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT d.trip_id FROM itinerary_items i
        JOIN itinerary_days d ON i.day_id = d.id
        WHERE i.id = %s
    """, (item_id,))
    row = cur.fetchone()
    cur.execute("DELETE FROM itinerary_items WHERE id = %s", (item_id,))
    mysql.connection.commit()
    cur.close()
    flash('Activity removed.', 'info')
    if row:
        return redirect(url_for('itinerary.builder', trip_id=row['trip_id']))
    return redirect(url_for('trips.list_trips'))

@itinerary_bp.route('/itinerary/day/<int:day_id>/delete', methods=['POST'])
@login_required
def delete_day(day_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT trip_id FROM itinerary_days WHERE id = %s", (day_id,))
    row = cur.fetchone()
    cur.execute("DELETE FROM itinerary_days WHERE id = %s", (day_id,))
    mysql.connection.commit()
    cur.close()
    flash('Day removed.', 'info')
    if row:
        return redirect(url_for('itinerary.builder', trip_id=row['trip_id']))
    return redirect(url_for('trips.list_trips'))
