import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'traveloop_secret_2024')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Sanju@8520')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'traveloop')
    MYSQL_CURSORCLASS = 'DictCursor'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload
