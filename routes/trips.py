from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from utils.decorators import login_required
from utils.helpers import is_valid_date_range, is_positive_number, generate_share_token, get_trip_status

trips_bp = Blueprint('trips', __name__)

@trips_bp.route('/trips')
@login_required
def list_trips():
    user_id = session['user_id']
    status_filter = request.args.get('status', 'all')
    cur = mysql.connection.cursor()

    if status_filter in ('upcoming', 'ongoing', 'completed'):
        cur.execute("""
            SELECT t.*, COALESCE(SUM(e.amount),0) as spent
            FROM trips t LEFT JOIN expenses e ON t.id = e.trip_id
            WHERE t.user_id = %s AND t.status = %s
            GROUP BY t.id ORDER BY t.start_date ASC
        """, (user_id, status_filter))
    else:
        cur.execute("""
            SELECT t.*, COALESCE(SUM(e.amount),0) as spent
            FROM trips t LEFT JOIN expenses e ON t.id = e.trip_id
            WHERE t.user_id = %s
            GROUP BY t.id ORDER BY t.start_date ASC
        """, (user_id,))

    trips = cur.fetchall()
    cur.close()
    return render_template('trips/list.html', trips=trips, status_filter=status_filter)

@trips_bp.route('/trips/create', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        destination = request.form.get('destination', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        description = request.form.get('description', '').strip()
        total_budget = request.form.get('total_budget', '0').strip()

        if not all([name, destination, start_date, end_date]):
            flash('Name, destination, and dates are required.', 'danger')
            return render_template('trips/create.html')

        if not is_valid_date_range(start_date, end_date):
            flash('End date must be on or after start date.', 'danger')
            return render_template('trips/create.html')

        if not is_positive_number(total_budget):
            flash('Budget must be a positive number.', 'danger')
            return render_template('trips/create.html')

        status = get_trip_status(start_date, end_date)
        token = generate_share_token()
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO trips (user_id, name, destination, start_date, end_date,
                               description, total_budget, status, share_token)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], name, destination, start_date, end_date,
              description, float(total_budget), status, token))
        mysql.connection.commit()
        trip_id = cur.lastrowid
        cur.close()

        flash('Trip created successfully!', 'success')
        return redirect(url_for('itinerary.builder', trip_id=trip_id))

    return render_template('trips/create.html')

@trips_bp.route('/trips/<int:trip_id>')
@login_required
def view_trip(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    cur.execute("SELECT * FROM itinerary_days WHERE trip_id = %s ORDER BY day_number", (trip_id,))
    days = [dict(row) for row in cur.fetchall()]
    for day in days:
        cur.execute("SELECT * FROM itinerary_items WHERE day_id = %s ORDER BY start_time", (day['id'],))
        day['items'] = cur.fetchall()

    cur.execute("SELECT SUM(amount) as total FROM expenses WHERE trip_id = %s", (trip_id,))
    spent = float(cur.fetchone()['total'] or 0)
    trip = dict(trip)
    trip['total_budget'] = float(trip['total_budget'] or 0)

    cur.close()
    return render_template('trips/view.html', trip=trip, days=days, spent=spent)

@trips_bp.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        destination = request.form.get('destination', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        description = request.form.get('description', '').strip()
        total_budget = request.form.get('total_budget', '0').strip()

        if not all([name, destination, start_date, end_date]):
            flash('Required fields missing.', 'danger')
            return render_template('trips/edit.html', trip=trip)

        if not is_valid_date_range(start_date, end_date):
            flash('Invalid date range.', 'danger')
            return render_template('trips/edit.html', trip=trip)

        status = get_trip_status(start_date, end_date)
        cur.execute("""
            UPDATE trips SET name=%s, destination=%s, start_date=%s, end_date=%s,
            description=%s, total_budget=%s, status=%s WHERE id=%s AND user_id=%s
        """, (name, destination, start_date, end_date, description,
              float(total_budget), status, trip_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        flash('Trip updated.', 'success')
        return redirect(url_for('trips.view_trip', trip_id=trip_id))

    cur.close()
    return render_template('trips/edit.html', trip=trip)

@trips_bp.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Trip deleted.', 'info')
    return redirect(url_for('trips.list_trips'))

@trips_bp.route('/trips/share/<token>')
def shared_trip(token):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE share_token = %s AND is_public = TRUE", (token,))
    trip = cur.fetchone()
    if not trip:
        flash('Shared trip not found or not public.', 'danger')
        return redirect(url_for('auth.login'))

    cur.execute("SELECT * FROM itinerary_days WHERE trip_id = %s ORDER BY day_number", (trip['id'],))
    days = [dict(row) for row in cur.fetchall()]
    for day in days:
        cur.execute("SELECT * FROM itinerary_items WHERE day_id = %s ORDER BY start_time", (day['id'],))
        day['items'] = cur.fetchall()

    cur.close()
    return render_template('trips/shared.html', trip=trip, days=days)

@trips_bp.route('/trips/<int:trip_id>/toggle_public', methods=['POST'])
@login_required
def toggle_public(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT is_public FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    if trip:
        new_val = not trip['is_public']
        cur.execute("UPDATE trips SET is_public = %s WHERE id = %s", (new_val, trip_id))
        mysql.connection.commit()
        flash('Trip visibility updated.', 'success')
    cur.close()
    return redirect(url_for('trips.view_trip', trip_id=trip_id))
