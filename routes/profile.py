from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from utils.decorators import login_required
from utils.helpers import is_valid_email

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def view():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.execute("SELECT * FROM trips WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    trips = cur.fetchall()
    cur.close()
    return render_template('profile/view.html', user=user, trips=trips)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()

        if not name or not email:
            flash('Name and email are required.', 'danger')
            return render_template('profile/edit.html', user=user)

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('profile/edit.html', user=user)

        cur.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, session['user_id']))
        if cur.fetchone():
            flash('Email already in use.', 'danger')
            return render_template('profile/edit.html', user=user)

        cur.execute("UPDATE users SET name = %s, email = %s WHERE id = %s",
                    (name, email, session['user_id']))
        mysql.connection.commit()
        session['user_name'] = name
        cur.close()
        flash('Profile updated.', 'success')
        return redirect(url_for('profile.view'))

    cur.close()
    return render_template('profile/edit.html', user=user)
