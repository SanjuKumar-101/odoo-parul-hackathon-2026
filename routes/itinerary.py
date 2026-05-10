from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import mysql
from utils.decorators import login_required
from utils.helpers import is_positive_number

itinerary_bp = Blueprint('itinerary', __name__)

def _get_trip_or_404(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    cur.close()
    return trip


def _get_city_info(city_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cities WHERE LOWER(name) = LOWER(%s)", (city_name,))
    city = cur.fetchone()
    cur.close()
    return city


def _get_days_with_items(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM itinerary_days WHERE trip_id = %s ORDER BY day_number", (trip_id,))
    days = [dict(row) for row in cur.fetchall()]
    total_cost = 0.0
    for day in days:
        cur.execute("SELECT * FROM itinerary_items WHERE day_id = %s ORDER BY start_time", (day['id'],))
        items = cur.fetchall()
        day['items'] = items
        day['day_total'] = sum(float(i['cost'] or 0) for i in items)
        total_cost += day['day_total']
    cur.close()
    return days, total_cost

@itinerary_bp.route('/trips/<int:trip_id>/itinerary')
@login_required
def builder(trip_id):
    trip = _get_trip_or_404(trip_id)
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))
    days, total_cost = _get_days_with_items(trip_id)
    city_info = _get_city_info(trip['destination'])
    return render_template('itinerary/builder.html', trip=trip, days=days,
                           total_cost=total_cost, city_info=city_info)

@itinerary_bp.route('/trips/<int:trip_id>/itinerary/view')
@login_required
def view(trip_id):
    trip = _get_trip_or_404(trip_id)
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    days, total_cost = _get_days_with_items(trip_id)
    trip = dict(trip)
    trip['total_budget'] = float(trip['total_budget'] or 0)

    # Itinerary category breakdown
    category_totals = {}
    for day in days:
        for item in day['items']:
            cat = item['category'] or 'general'
            category_totals[cat] = category_totals.get(cat, 0) + float(item['cost'] or 0)

    # Expense data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM expenses WHERE trip_id = %s ORDER BY expense_date DESC", (trip_id,))
    expenses = cur.fetchall()

    cur.execute("SELECT SUM(amount) as total FROM expenses WHERE trip_id = %s", (trip_id,))
    total_spent = float(cur.fetchone()['total'] or 0)

    cur.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses WHERE trip_id = %s GROUP BY category
    """, (trip_id,))
    by_category = cur.fetchall()
    cur.close()

    remaining = trip['total_budget'] - total_spent
    city_info = _get_city_info(trip['destination'])

    return render_template('itinerary/view.html', trip=trip, days=days,
                           total_cost=total_cost, category_totals=category_totals,
                           expenses=expenses, total_spent=total_spent,
                           by_category=by_category, remaining=remaining,
                           city_info=city_info)

@itinerary_bp.route('/trips/<int:trip_id>/itinerary/add_expense', methods=['POST'])
@login_required
def add_expense(trip_id):
    title = request.form.get('title', '').strip()
    amount = request.form.get('amount', '').strip()
    category = request.form.get('category', 'general').strip()
    expense_date = request.form.get('expense_date', '') or None
    notes = request.form.get('notes', '').strip()

    if not title or not amount or not is_positive_number(amount):
        flash('Valid title and amount are required.', 'danger')
        return redirect(url_for('itinerary.view', trip_id=trip_id))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO expenses (trip_id, title, amount, category, expense_date, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (trip_id, title, float(amount), category, expense_date, notes))
    mysql.connection.commit()
    cur.close()
    flash('Expense added.', 'success')
    return redirect(url_for('itinerary.view', trip_id=trip_id) + '#budget')

@itinerary_bp.route('/trips/<int:trip_id>/itinerary/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(trip_id, expense_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s AND trip_id = %s", (expense_id, trip_id))
    mysql.connection.commit()
    cur.close()
    flash('Expense removed.', 'info')
    return redirect(url_for('itinerary.view', trip_id=trip_id) + '#budget')

@itinerary_bp.route('/trips/<int:trip_id>/itinerary/add_day', methods=['POST'])
@login_required
def add_day(trip_id):
    trip = _get_trip_or_404(trip_id)
    if not trip:
        return jsonify({'error': 'Not found'}), 404

    requested_city = request.form.get('city', '').strip()
    city = trip['destination']
    day_date = request.form.get('day_date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not day_date:
        flash('Day date is required.', 'danger')
        return redirect(url_for('itinerary.builder', trip_id=trip_id))

    if requested_city and requested_city.lower() != trip['destination'].lower():
        flash(f'Itinerary city must match this trip destination: {trip["destination"]}.', 'danger')
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
