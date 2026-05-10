from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from utils.decorators import login_required

checklist_bp = Blueprint('checklist', __name__)

@checklist_bp.route('/trips/<int:trip_id>/checklist')
@login_required
def view(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    cur.execute("SELECT * FROM packing_items WHERE trip_id = %s ORDER BY category, item_name", (trip_id,))
    items = cur.fetchall()
    cur.close()

    # Group by category
    grouped = {}
    for item in items:
        cat = item['category'] or 'general'
        grouped.setdefault(cat, []).append(item)

    return render_template('checklist/view.html', trip=trip, grouped=grouped)

@checklist_bp.route('/trips/<int:trip_id>/checklist/add', methods=['POST'])
@login_required
def add_item(trip_id):
    item_name = request.form.get('item_name', '').strip()
    category = request.form.get('category', 'general').strip()

    if not item_name:
        flash('Item name is required.', 'danger')
        return redirect(url_for('checklist.view', trip_id=trip_id))

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO packing_items (trip_id, item_name, category) VALUES (%s, %s, %s)",
                (trip_id, item_name, category))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('checklist.view', trip_id=trip_id))

@checklist_bp.route('/trips/<int:trip_id>/checklist/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_item(trip_id, item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT is_packed FROM packing_items WHERE id = %s AND trip_id = %s", (item_id, trip_id))
    item = cur.fetchone()
    if item:
        cur.execute("UPDATE packing_items SET is_packed = %s WHERE id = %s",
                    (not item['is_packed'], item_id))
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('checklist.view', trip_id=trip_id))

@checklist_bp.route('/trips/<int:trip_id>/checklist/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(trip_id, item_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM packing_items WHERE id = %s AND trip_id = %s", (item_id, trip_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('checklist.view', trip_id=trip_id))
