import os
import logging
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_mail import Mail

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

# Create Flask app
app = Flask(__name__)

# Configure app
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure middleware
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

# Add utility functions to Jinja templates
@app.context_processor
def utility_processor():
    def now():
        return datetime.datetime.now()
    return dict(now=now)

# Configure login manager
login_manager.login_view = 'auth.sign_in'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Create database tables
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    from .models import User, MFAToken, PasswordResetToken, EmailVerificationToken
    db.create_all()

# Import and register blueprints
from .auth import auth_bp
app.register_blueprint(auth_bp)

# Load user from user_id stored in the session
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    from flask import redirect, url_for
    return redirect(url_for('auth.sign_in'))
