import os
import logging
import datetime

from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import MetaData
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
db = SQLAlchemy(metadata=MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
}))

# Initialize extensions 
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure app based on environment
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
    else:
        app.config.from_object('config.Config')
        app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    
    # Configure middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.sign_in'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Add utility functions to Jinja templates
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.datetime.now()
        return dict(now=now)
    
    # Import and register blueprints
    from .auth import auth_bp
    from .dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    
    # Load user from user_id stored in the session
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    # Routes
    @app.route('/')
    def index():
        from flask import render_template, redirect, url_for
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            return redirect(url_for('auth.sign_in'))
        
        return redirect(url_for('home.html'))
    
    @app.route('/tutorials')
    def tutorials():
        from flask import render_template, redirect, url_for
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            return redirect(url_for('auth.sign_in'))
        
        return render_template('tutorials.html')

    from app.models.user import ShareUser

    @app.context_processor
    def inject_shareuser():
        return dict(ShareUser=ShareUser)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

# Create the application instance
app = create_app()