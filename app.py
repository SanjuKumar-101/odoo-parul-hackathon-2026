import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.trips import trips_bp
    from routes.itinerary import itinerary_bp
    from routes.budget import budget_bp
    from routes.checklist import checklist_bp
    from routes.notes import notes_bp
    from routes.profile import profile_bp
    from routes.community import community_bp
    from routes.admin import admin_bp
    from routes.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(checklist_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(search_bp)

    register_error_handlers(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config.get('DEBUG', False))
