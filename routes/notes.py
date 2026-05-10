from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from utils.decorators import login_required

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/trips/<int:trip_id>/notes')
@login_required
def view(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    cur.execute("""
        SELECT n.*, d.day_date, d.city FROM trip_notes n
        LEFT JOIN itinerary_days d ON n.day_id = d.id
        WHERE n.trip_id = %s ORDER BY n.created_at DESC
    """, (trip_id,))
    notes = cur.fetchall()

    cur.execute("SELECT * FROM itinerary_days WHERE trip_id = %s ORDER BY day_number", (trip_id,))
    days = cur.fetchall()
    cur.close()

    return render_template('notes/view.html', trip=trip, notes=notes, days=days)

@notes_bp.route('/trips/<int:trip_id>/notes/add', methods=['POST'])
@login_required
def add_note(trip_id):
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    day_id = request.form.get('day_id') or None

    if not content:
        flash('Note content is required.', 'danger')
        return redirect(url_for('notes.view', trip_id=trip_id))

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO trip_notes (trip_id, day_id, title, content) VALUES (%s, %s, %s, %s)",
                (trip_id, day_id, title, content))
    mysql.connection.commit()
    cur.close()
    flash('Note saved.', 'success')
    return redirect(url_for('notes.view', trip_id=trip_id))

@notes_bp.route('/trips/<int:trip_id>/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(trip_id, note_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM trip_notes WHERE id = %s AND trip_id = %s", (note_id, trip_id))
    mysql.connection.commit()
    cur.close()
    flash('Note deleted.', 'info')
    return redirect(url_for('notes.view', trip_id=trip_id))
