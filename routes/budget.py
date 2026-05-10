from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from utils.decorators import login_required
from utils.helpers import is_positive_number

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/trips/<int:trip_id>/budget')
@login_required
def view(trip_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trips WHERE id = %s AND user_id = %s", (trip_id, session['user_id']))
    trip = cur.fetchone()
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('trips.list_trips'))

    cur.execute("SELECT * FROM budgets WHERE trip_id = %s", (trip_id,))
    budgets = cur.fetchall()

    cur.execute("SELECT * FROM expenses WHERE trip_id = %s ORDER BY expense_date DESC", (trip_id,))
    expenses = cur.fetchall()

    cur.execute("SELECT SUM(amount) as total FROM expenses WHERE trip_id = %s", (trip_id,))
    total_spent = cur.fetchone()['total'] or 0

    cur.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses WHERE trip_id = %s GROUP BY category
    """, (trip_id,))
    by_category = cur.fetchall()

    cur.close()
    remaining = float(trip['total_budget']) - float(total_spent)
    return render_template('budget/view.html',
                           trip=trip, budgets=budgets, expenses=expenses,
                           total_spent=total_spent, remaining=remaining,
                           by_category=by_category)

@budget_bp.route('/trips/<int:trip_id>/expenses/add', methods=['POST'])
@login_required
def add_expense(trip_id):
    title = request.form.get('title', '').strip()
    amount = request.form.get('amount', '').strip()
    category = request.form.get('category', 'general').strip()
    expense_date = request.form.get('expense_date', '') or None
    notes = request.form.get('notes', '').strip()

    if not title or not amount:
        flash('Title and amount are required.', 'danger')
        return redirect(url_for('budget.view', trip_id=trip_id))

    if not is_positive_number(amount):
        flash('Amount must be a positive number.', 'danger')
        return redirect(url_for('budget.view', trip_id=trip_id))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO expenses (trip_id, title, amount, category, expense_date, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (trip_id, title, float(amount), category, expense_date, notes))
    mysql.connection.commit()
    cur.close()
    flash('Expense added.', 'success')
    return redirect(url_for('budget.view', trip_id=trip_id))

@budget_bp.route('/trips/<int:trip_id>/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(trip_id, expense_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s AND trip_id = %s", (expense_id, trip_id))
    mysql.connection.commit()
    cur.close()
    flash('Expense removed.', 'info')
    return redirect(url_for('budget.view', trip_id=trip_id))
