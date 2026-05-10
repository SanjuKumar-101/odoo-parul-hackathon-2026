import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import mysql
from utils.decorators import login_required
from utils.helpers import is_valid_email
from config import Config

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_storage_is_read_only():
    upload_folder = os.path.abspath(Config.UPLOAD_FOLDER)
    app_root = os.path.abspath(os.getcwd())

    return (
        os.getenv('VERCEL') == '1'
        or bool(os.getenv('VERCEL_ENV'))
        or bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME'))
        or bool(os.getenv('LAMBDA_TASK_ROOT'))
        or upload_folder.startswith('/var/task')
        or app_root.startswith('/var/task')
    )

@profile_bp.route('/profile')
@login_required
def view():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    cur.execute("SELECT COUNT(*) as total FROM trips WHERE user_id = %s", (session['user_id'],))
    total_trips = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as cnt FROM trips WHERE user_id = %s AND status='completed'", (session['user_id'],))
    completed = cur.fetchone()['cnt']

    cur.execute("SELECT COALESCE(SUM(total_budget),0) as total FROM trips WHERE user_id = %s", (session['user_id'],))
    total_budget = float(cur.fetchone()['total'])

    cur.execute("SELECT * FROM trips WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    trips = cur.fetchall()
    cur.close()
    return render_template('profile/view.html', user=user, trips=trips,
                           total_trips=total_trips, completed=completed,
                           total_budget=total_budget)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        tagline  = request.form.get('tagline', '').strip()
        bio      = request.form.get('bio', '').strip()
        location = request.form.get('location', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

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

        # Handle password change
        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('profile/edit.html', user=user)
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('profile/edit.html', user=user)
            hashed = generate_password_hash(new_password)
            cur.execute("UPDATE users SET password_hash = %s WHERE id = %s",
                        (hashed, session['user_id']))
            mysql.connection.commit()

        # Handle photo upload
        photo_path = user['profile_photo']
        file = request.files.get('profile_photo')
        image_upload_disabled = False
        if file and file.filename:
            if upload_storage_is_read_only():
                image_upload_disabled = True
            elif allowed_file(file.filename):
                filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
                upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'profiles')
                try:
                    os.makedirs(upload_dir, exist_ok=True)
                    file.save(os.path.join(upload_dir, filename))
                    photo_path = f"images/profiles/{filename}"
                except OSError:
                    image_upload_disabled = True
            else:
                flash('Unsupported image format. Please upload JPG, PNG, or WEBP.', 'warning')

        cur.execute("""
            UPDATE users SET name=%s, email=%s, tagline=%s, bio=%s,
            location=%s, profile_photo=%s WHERE id=%s
        """, (name, email, tagline, bio, location, photo_path, session['user_id']))
        mysql.connection.commit()
        session['user_name'] = name
        cur.close()
        if image_upload_disabled:
            flash('Profile details updated. Image upload is disabled on this deployment.', 'warning')
        else:
            flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile.view'))

    cur.close()
    return render_template('profile/edit.html', user=user)
