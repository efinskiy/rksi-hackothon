from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_manager
from datetime import timedelta
from flask_socketio import SocketIO

from .secrets import DB_PATH, SECRET_KEY

socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365*2)
    app.secret_key = SECRET_KEY

    
    
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_get'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
