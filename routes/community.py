from flask import Blueprint, render_template
from app import mysql

community_bp = Blueprint('community', __name__)

@community_bp.route('/community')
def index():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.*, u.name as author FROM trips t
        JOIN users u ON t.user_id = u.id
        WHERE t.is_public = TRUE
        ORDER BY t.created_at DESC LIMIT 20
    """)
    trips = cur.fetchall()
    cur.close()
    return render_template('community/index.html', trips=trips)
