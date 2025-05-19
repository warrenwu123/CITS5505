import datetime
import pyotp
from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from .activity import ActivitySession, ActivityRecord

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    is_active = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    has_mfa = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    total_duration = db.Column(db.Float, default=0.0)
    name = db.Column(db.String(100), nullable=True)  # 用户名字
    bio = db.Column(db.Text, nullable=True)  # 用户自我介绍
    
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
    # 添加分享权限关系
    shared_with = db.relationship('ShareUser',
                                 foreign_keys='ShareUser.user_id',
                                 backref=db.backref('user', lazy='joined'),
                                 lazy='dynamic',
                                 cascade="all, delete-orphan")
    shared_by = db.relationship('ShareUser',
                               foreign_keys='ShareUser.shared_user_id',
                               backref=db.backref('shared_user', lazy='joined'),
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
    
    @property
    def total_duration(self):
        """Calculate total training duration in minutes for all completed activity sessions"""
        total = db.session.query(func.sum(ActivitySession.duration))\
            .filter(ActivitySession.user_id == self.id,
                   ActivitySession.is_completed == True,
                   ActivitySession.duration.isnot(None))\
            .scalar()
        return total or 0  # Return 0 if no sessions or all durations are None

    def get_total_duration(self):
        from app.models import ActivityRecord, ActivitySession  
        total_minutes = (
            db.session.query(db.func.sum(ActivityRecord.actual_duration))
            .join(ActivitySession)
            .filter(ActivitySession.user_id == self.id)
            .scalar()
        )
        if not total_minutes:
            return "0m"
        hours = total_minutes // 3600
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"

    def get_total_calories(self):
        from app.models import ActivityRecord, ActivitySession
        total_calories = (
            db.session.query(db.func.sum(ActivitySession.calories_burned))
            .filter(
                ActivitySession.user_id == self.id,
                ActivitySession.is_completed == True
            )
            .scalar()
        )
        return int(total_calories) if total_calories else 0

    

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


class ShareUser(db.Model):
    """记录用户分享权限的表"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 被分享的用户
    shared_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 获得分享权限的用户
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<ShareUser {self.user_id} -> {self.shared_user_id}>'
    
    @staticmethod
    def can_view_profile(user_id, viewer_id):
        """检查viewer_id是否有权限查看user_id的信息"""
        if user_id == viewer_id:  # 用户总是可以查看自己的信息
            return True
        return ShareUser.query.filter_by(
            user_id=user_id,
            shared_user_id=viewer_id
        ).first() is not None