from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from utils.helpers import is_valid_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/login.html')

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('auth/login.html')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = user.get('is_admin', False)
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard.index'))

        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            cur.close()
            return render_template('auth/register.html')

        hashed = generate_password_hash(password)
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                    (name, email, hashed))
        mysql.connection.commit()
        cur.close()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
