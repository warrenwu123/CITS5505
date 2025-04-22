import os
class Config:
    """Application configuration class"""
    
    # Flask config
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///auth.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mail config
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'yes', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Auth config
    PASSWORD_RESET_EXPIRES = 3600  # 1 hour in seconds
    EMAIL_VERIFICATION_EXPIRES = 86400  # 24 hours in seconds
    MFA_CODE_EXPIRES = 300  # 5 minutes in seconds
    
    # App config
    APP_NAME = 'Flask Auth'
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
