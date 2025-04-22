from flask import render_template, current_app
from flask_mail import Message
from app import mail

def send_email(recipient, subject, html_body, text_body=None):
    """
    Send an email using Flask-Mail
    
    Args:
        recipient (str): Recipient email address
        subject (str): Email subject
        html_body (str): HTML version of the email
        text_body (str, optional): Text version of the email
    """
    msg = Message(
        subject=subject,
        recipients=[recipient],
        html=html_body,
        body=text_body or html_body
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_verification_email(user, token):
    """
    Send email verification link
    
    Args:
        user (User): User model instance
        token (str): Verification token
    """
    verify_url = f"{current_app.config['APP_URL']}/verify-email/{token}"
    
    subject = f"Verify your email address for {current_app.config['APP_NAME']}"
    html_body = render_template(
        'email/verify_email.html',
        user=user,
        verify_url=verify_url,
        app_name=current_app.config['APP_NAME']
    )
    
    return send_email(user.email, subject, html_body)

def send_reset_password_email(user, token):
    """
    Send password reset email
    
    Args:
        user (User): User model instance
        token (str): Password reset token
    """
    reset_url = f"{current_app.config['APP_URL']}/reset-password/{token}"
    
    subject = f"Reset your password for {current_app.config['APP_NAME']}"
    html_body = render_template(
        'email/reset_password.html',
        user=user,
        reset_url=reset_url,
        app_name=current_app.config['APP_NAME']
    )
    
    return send_email(user.email, subject, html_body)
