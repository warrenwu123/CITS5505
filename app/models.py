import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    is_active = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    has_mfa = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    
    # Relationships
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True)
    email_verification_tokens = db.relationship('EmailVerificationToken', backref='user', lazy=True)
    mfa_tokens = db.relationship('MFAToken', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token}>'
    
class EmailVerificationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<EmailVerificationToken {self.token}>'
    
class MFAToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(6), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<MFAToken {self.token}>'
