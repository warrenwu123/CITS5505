import datetime
import secrets
import string
import uuid
import pyotp
import io
import qrcode
import base64
from urllib.parse import urlencode
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from app import db
from .models import User, PasswordResetToken, EmailVerificationToken, MFAToken
from .forms import SignInForm, SignUpForm, ForgotPasswordForm, ResetPasswordForm, MFASetupForm, MFAVerifyForm, ProfilePictureForm 
from .email_utils import send_reset_password_email, send_verification_email
from .utils import save_profile_picture

auth_bp = Blueprint('auth', __name__)

def generate_token(length=32):
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@auth_bp.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    """Handle user sign in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.profile'))
    
    form = SignInForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid email or password', 'danger')
            return render_template('sign_in.html', form=form)
        
        if not user.is_email_verified:
            flash('Please verify your email before signing in', 'warning')
            return render_template('sign_in.html', form=form)
        
        # Store user ID in session for MFA verification
        if user.has_mfa:
            session['user_id_for_mfa'] = user.id
            session['remember_me'] = form.remember_me.data
            return redirect(url_for('auth.verify_mfa'))
        
        login_user(user, remember=form.remember_me.data)
        flash('Signed in successfully!', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.profile'))
    
    return render_template('sign_in.html', form=form)

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.profile'))
    
    form = SignUpForm()
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        
        user = User(
            email=form.email.data,
            password_hash=hashed_password,
            is_active=True,
            is_email_verified=False,
            has_mfa=False
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Generate email verification token
            token = generate_token()
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=current_app.config['EMAIL_VERIFICATION_EXPIRES']
            )
            
            email_token = EmailVerificationToken(
                token=token,
                user_id=user.id,
                expires_at=expires
            )
            
            db.session.add(email_token)
            db.session.commit()
            
            # For testing purposes: Auto-verify the email (replace with email sending in production)
            # Uncomment the line below to send verification emails in production
            # send_verification_email(user, token)
            
            # For testing: auto-verify the account
            user.is_email_verified = True
            db.session.commit()
            
            flash('Account created successfully! Your email has been automatically verified for testing.', 'success')
            return redirect(url_for('auth.sign_in'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Email address already registered', 'danger')
    
    return render_template('sign_up.html', form=form)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user email with token"""
    email_token = EmailVerificationToken.query.filter_by(token=token).first()
    
    if not email_token or email_token.is_expired():
        flash('Invalid or expired verification link', 'danger')
        return redirect(url_for('auth.sign_in'))
    
    user = User.query.get(email_token.user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.sign_in'))
    
    user.is_email_verified = True
    db.session.delete(email_token)
    db.session.commit()
    
    flash('Email verified successfully! You can now sign in.', 'success')
    return redirect(url_for('auth.sign_in'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.profile'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Clear any existing tokens for this user
            PasswordResetToken.query.filter_by(user_id=user.id).delete()
            
            # Create new token
            token = generate_token()
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=current_app.config['PASSWORD_RESET_EXPIRES']
            )
            
            reset_token = PasswordResetToken(
                token=token,
                user_id=user.id,
                expires_at=expires
            )
            
            db.session.add(reset_token)
            db.session.commit()
            
            # Send password reset email
            send_reset_password_email(user, token)
        
        # Always show success message to prevent email enumeration
        flash('If your email is registered, you will receive a password reset link shortly.', 'info')
        return redirect(url_for('auth.sign_in'))
    
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.profile'))
    
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token or reset_token.is_expired():
        flash('Invalid or expired reset link', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    form.token.data = token
    
    if form.validate_on_submit():
        user = User.query.get(reset_token.user_id)
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('auth.sign_in'))
        
        # Update user password
        user.password_hash = generate_password_hash(form.password.data)
        
        # Remove used token
        db.session.delete(reset_token)
        db.session.commit()
        
        flash('Password updated successfully! You can now sign in with your new password.', 'success')
        return redirect(url_for('auth.sign_in'))
    
    return render_template('reset_password.html', form=form)

@auth_bp.route('/setup-mfa', methods=['GET', 'POST'])
@login_required
def setup_mfa():
    """Set up multi-factor authentication"""
    if current_user.has_mfa:
        flash('MFA is already enabled for your account', 'info')
        return redirect(url_for('dashboard.profile'))
    
    form = MFASetupForm()
    
    # Generate TOTP secret if not already done
    if 'mfa_secret' not in session:
        session['mfa_secret'] = pyotp.random_base32()
    
    # Generate QR code
    totp = pyotp.TOTP(session['mfa_secret'])
    uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name=current_app.config['APP_NAME']
    )
    
    qr = qrcode.make(uri)
    buffered = io.BytesIO()
    qr.save(buffered)
    qr_code = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    if form.validate_on_submit():
        # Store secret in user record
        current_user.mfa_secret = session['mfa_secret']
        current_user.has_mfa = True
        db.session.commit()
        
        # Clean up session
        session.pop('mfa_secret', None)
        
        flash('Multi-factor authentication has been enabled for your account!', 'success')
        return redirect(url_for('dashboard.profile'))
    
    return render_template('setup_mfa.html', form=form, qr_code=qr_code, secret=session['mfa_secret'])

@auth_bp.route('/verify-mfa', methods=['GET', 'POST'])
def verify_mfa():
    """Verify MFA code during login"""
    # Ensure there is a user to verify
    if 'user_id_for_mfa' not in session:
        return redirect(url_for('auth.sign_in'))
    
    user = User.query.get(session['user_id_for_mfa'])
    
    if not user:
        session.pop('user_id_for_mfa', None)
        session.pop('remember_me', None)
        flash('User not found', 'danger')
        return redirect(url_for('auth.sign_in'))
    
    form = MFAVerifyForm()
    
    if form.validate_on_submit():
        # Verify TOTP code
        totp = pyotp.TOTP(user.mfa_secret)
        
        if totp.verify(form.code.data):
            # Clean up session
            user_id = session.pop('user_id_for_mfa', None)
            remember = session.pop('remember_me', False)
            
            # Log in user
            login_user(user, remember=remember)
            flash('Signed in successfully!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.profile'))
        else:
            flash('Invalid authentication code', 'danger')
    
    return render_template('verify_mfa.html', form=form)

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfilePictureForm()

    if request.method == 'POST' and form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.profile_image = picture_file
            db.session.commit()

            flash('Profile picture updated!', 'success')
            return redirect(url_for('auth.profile'))

    return render_template('profile.html', form=form)

@auth_bp.route('/sign-out')
@login_required
def sign_out():
    """Sign out the current user"""
    logout_user()
    flash('You have been signed out successfully', 'success')
    return redirect(url_for('auth.sign_in'))

@auth_bp.route('/resend-verification')
def resend_verification():
    """Resend email verification link"""
    email = request.args.get('email')
    
    if not email:
        flash('Email is required', 'danger')
        return redirect(url_for('auth.sign_in'))
    
    user = User.query.filter_by(email=email).first()
    
    if user and not user.is_email_verified:
        # Clear any existing tokens for this user
        EmailVerificationToken.query.filter_by(user_id=user.id).delete()
        
        # Create new token
        token = generate_token()
        expires = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=current_app.config['EMAIL_VERIFICATION_EXPIRES']
        )
        
        email_token = EmailVerificationToken(
            token=token,
            user_id=user.id,
            expires_at=expires
        )
        
        db.session.add(email_token)
        db.session.commit()
        
        # Send verification email
        send_verification_email(user, token)
    
    # Always show success message to prevent email enumeration
    flash('If your email is registered and unverified, you will receive a new verification link shortly.', 'info')
    return redirect(url_for('auth.sign_in'))

@auth_bp.route('/disable-mfa')
@login_required
def disable_mfa():
    """Disable MFA for the current user"""
    if not current_user.has_mfa:
        flash('MFA is not enabled for your account', 'info')
        return redirect(url_for('dashboard.profile'))
    
    current_user.has_mfa = False
    current_user.mfa_secret = None
    db.session.commit()
    
    flash('Multi-factor authentication has been disabled for your account.', 'success')
    return redirect(url_for('dashboard.profile'))
