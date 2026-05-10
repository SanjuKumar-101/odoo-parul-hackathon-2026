import re
from datetime import datetime

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def is_valid_date_range(start, end):
    try:
        s = datetime.strptime(start, '%Y-%m-%d')
        e = datetime.strptime(end, '%Y-%m-%d')
        return e >= s
    except ValueError:
        return False

def is_positive_number(value):
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False

def generate_share_token():
    import secrets
    return secrets.token_urlsafe(16)

def get_trip_status(start_date, end_date):
    today = datetime.today().date()
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    if today < start_date:
        return 'upcoming'
    elif today > end_date:
        return 'completed'
    return 'ongoing'
