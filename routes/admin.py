from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) as total FROM users WHERE is_admin = FALSE")
    total_users = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM trips")
    total_trips = cur.fetchone()['total']

    cur.execute("SELECT COALESCE(SUM(total_budget), 0) as total FROM trips")
    total_budget = cur.fetchone()['total']

    cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM expenses")
    total_expenses = cur.fetchone()['total']

    cur.execute("SELECT status, COUNT(*) as cnt FROM trips GROUP BY status")
    trip_by_status = cur.fetchall()

    cur.execute("""
        SELECT destination as name, COUNT(*) as trip_count
        FROM trips WHERE destination IS NOT NULL AND destination != ''
        GROUP BY destination ORDER BY trip_count DESC LIMIT 6
    """)
    top_cities = cur.fetchall()

    cur.execute("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as cnt
        FROM trips GROUP BY month ORDER BY month ASC LIMIT 6
    """)
    trips_by_month = cur.fetchall()

    cur.execute("""
        SELECT u.id, u.name, u.email, u.created_at, u.is_admin,
               COUNT(t.id) as trip_count
        FROM users u LEFT JOIN trips t ON u.id = t.user_id
        GROUP BY u.id ORDER BY u.created_at DESC
    """)
    users = cur.fetchall()

    cur.execute("""
        SELECT category, COALESCE(SUM(amount), 0) as total
        FROM expenses GROUP BY category
    """)
    expenses_by_category = cur.fetchall()

    cur.execute("""
        SELECT t.id, t.name, t.destination, t.status, t.total_budget,
               t.start_date, t.end_date, u.name as user_name
        FROM trips t JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC LIMIT 10
    """)
    recent_trips = cur.fetchall()

    cur.close()
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_trips=total_trips,
                           total_budget=total_budget,
                           total_expenses=total_expenses,
                           trip_by_status=trip_by_status,
                           top_cities=top_cities,
                           trips_by_month=trips_by_month,
                           users=users,
                           expenses_by_category=expenses_by_category,
                           recent_trips=recent_trips)

@admin_bp.route('/users')
@admin_required
def users():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.id, u.name, u.email, u.is_admin, u.created_at,
               COUNT(t.id) as trip_count
        FROM users u LEFT JOIN trips t ON u.id = t.user_id
        GROUP BY u.id ORDER BY u.created_at DESC
    """)
    users = cur.fetchall()
    cur.close()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    if user_id == session['user_id']:
        flash('You cannot change your own admin status.', 'danger')
        return redirect(url_for('admin.users'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if user:
        cur.execute("UPDATE users SET is_admin = %s WHERE id = %s",
                    (not user['is_admin'], user_id))
        mysql.connection.commit()
        flash('User admin status updated.', 'success')
    cur.close()
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    flash('User deleted.', 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/trips')
@admin_required
def trips():
    status = request.args.get('status', 'all')
    cur = mysql.connection.cursor()
    if status in ('upcoming', 'ongoing', 'completed'):
        cur.execute("""
            SELECT t.*, u.name as user_name FROM trips t
            JOIN users u ON t.user_id = u.id
            WHERE t.status = %s ORDER BY t.created_at DESC
        """, (status,))
    else:
        cur.execute("""
            SELECT t.*, u.name as user_name FROM trips t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
        """)
    trips = cur.fetchall()
    cur.close()
    return render_template('admin/trips.html', trips=trips, status_filter=status)

@admin_bp.route('/trips/<int:trip_id>/delete', methods=['POST'])
@admin_required
def delete_trip(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM trips WHERE id = %s", (trip_id,))
    mysql.connection.commit()
    cur.close()
    flash('Trip deleted.', 'info')
    return redirect(url_for('admin.trips'))

@admin_bp.route('/cities')
@admin_required
def cities():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cities ORDER BY popularity DESC")
    cities = cur.fetchall()
    cur.close()
    return render_template('admin/cities.html', cities=cities)

@admin_bp.route('/cities/add', methods=['POST'])
@admin_required
def add_city():
    name = request.form.get('name', '').strip()
    country = request.form.get('country', '').strip()
    region = request.form.get('region', '').strip()
    cost_index = request.form.get('cost_index', '1.0').strip()
    popularity = request.form.get('popularity', '0').strip()

    if not name or not country:
        flash('Name and country are required.', 'danger')
        return redirect(url_for('admin.cities'))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO cities (name, country, region, cost_index, popularity)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, country, region, float(cost_index), int(popularity)))
    mysql.connection.commit()
    cur.close()
    flash(f'City {name} added.', 'success')
    return redirect(url_for('admin.cities'))

@admin_bp.route('/cities/<int:city_id>/delete', methods=['POST'])
@admin_required
def delete_city(city_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cities WHERE id = %s", (city_id,))
    mysql.connection.commit()
    cur.close()
    flash('City deleted.', 'info')
    return redirect(url_for('admin.cities'))
