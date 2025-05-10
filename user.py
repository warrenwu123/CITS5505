import datetime
import pyotp
from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    is_active = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    has_mfa = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
<<<<<<< HEAD
    total_duration = db.Column(db.Float, default=0.0)  # 总锻炼时长（分钟）
=======
>>>>>>> upstream/master
    # Removed avatar_url to maintain compatibility with existing database
    
    # Relationships
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True)
    email_verification_tokens = db.relationship('EmailVerificationToken', backref='user', lazy=True)
    mfa_tokens = db.relationship('MFAToken', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True, cascade="all, delete-orphan")
    activity_sessions = db.relationship('ActivitySession', backref='user', lazy=True, cascade="all, delete-orphan")
    user_achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade="all, delete-orphan")
    followers = db.relationship('Follow', 
                               foreign_keys='Follow.followed_id',
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic', 
                               cascade="all, delete-orphan")
    following = db.relationship('Follow',
                               foreign_keys='Follow.follower_id',
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_mfa_secret(self):
        self.mfa_secret = pyotp.random_base32()
        return self.mfa_secret
    
    def get_totp_uri(self):
        # For Google Authenticator or similar apps
        return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.email,
            issuer_name="FitTrack"
        )
    
    def verify_totp(self, token):
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token)
    
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
            return True
        return False
    
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            return True
        return False
    
    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None
    
    def get_followers_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.following.count()
    

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


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    follow_date = db.Column(db.DateTime, default=func.now())
    
    def __repr__(self):
        return f'<Follow {self.follower_id} -> {self.followed_id}>'