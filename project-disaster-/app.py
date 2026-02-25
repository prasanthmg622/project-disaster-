from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User

socketio = SocketIO()
login = LoginManager()
login.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)
    login.init_app(app)
    socketio.init_app(app)

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from routes.alerts import alerts_bp
    app.register_blueprint(alerts_bp)

    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Background Tasks
    from apscheduler.schedulers.background import BackgroundScheduler
    from services.disaster_apis import fetch_usgs_earthquakes

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: fetch_usgs_earthquakes_with_app(app), trigger="interval", minutes=10)
    scheduler.start()

    return app

def fetch_usgs_earthquakes_with_app(app):
    with app.app_context():
        from services.disaster_apis import fetch_usgs_earthquakes
        fetch_usgs_earthquakes()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
