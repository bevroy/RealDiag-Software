"""
Email Verification Service
===========================

Handles email verification for employee accounts.
"""

import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@realdiag.org")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://realdiag.netlify.app")

# Token expiration (24 hours)
TOKEN_EXPIRATION_HOURS = 24


def is_employee_email(email: str) -> bool:
    """
    Check if email is from realdiag.org domain.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email ends with @realdiag.org
    """
    return email.lower().endswith("@realdiag.org")


def generate_verification_token() -> str:
    """
    Generate a secure random verification token.
    
    Returns:
        32-character hex token
    """
    return secrets.token_urlsafe(32)


def is_token_expired(sent_at: datetime) -> bool:
    """
    Check if verification token has expired.
    
    Args:
        sent_at: When the token was sent
        
    Returns:
        True if token is expired (>24 hours old)
    """
    if not sent_at:
        return True
    expiration = sent_at + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    return datetime.utcnow() > expiration


def send_verification_email(email: str, token: str, full_name: Optional[str] = None) -> bool:
    """
    Send email verification link to employee.
    
    Args:
        email: Employee email address
        token: Verification token
        full_name: User's full name (optional)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("Email not configured - skipping verification email")
        logger.info(f"Verification link: {FRONTEND_URL}/verify-email?token={token}")
        return False
    
    try:
        # Create verification link
        verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Verify your RealDiag employee account"
        msg["From"] = FROM_EMAIL
        msg["To"] = email
        
        # Plain text version
        text_content = f"""
Hi {full_name or 'there'},

Welcome to RealDiag! Please verify your employee email address by clicking the link below:

{verification_url}

This link will expire in {TOKEN_EXPIRATION_HOURS} hours.

If you didn't create a RealDiag account, please ignore this email.

Best regards,
The RealDiag Team
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to RealDiag!</h1>
        </div>
        <div class="content">
            <p>Hi {full_name or 'there'},</p>
            
            <p>Thank you for joining RealDiag as an employee! Please verify your email address to activate your account and access all premium features.</p>
            
            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #fff; padding: 10px; border-radius: 5px;">{verification_url}</p>
            
            <p><strong>This link will expire in {TOKEN_EXPIRATION_HOURS} hours.</strong></p>
            
            <p>If you didn't create a RealDiag account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2025 RealDiag. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach both versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Verification email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False


def send_welcome_email(email: str, full_name: Optional[str] = None) -> bool:
    """
    Send welcome email after successful verification.
    
    Args:
        email: Employee email address
        full_name: User's full name (optional)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("Email not configured - skipping welcome email")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your RealDiag employee account is active!"
        msg["From"] = FROM_EMAIL
        msg["To"] = email
        
        # Plain text version
        text_content = f"""
Hi {full_name or 'there'},

Your RealDiag employee account has been verified and is now active!

You now have full access to all RealDiag features:
• Unlimited diagnostic searches
• All clinical modules
• EHR integration
• API access
• Analytics dashboard
• Priority support

Start exploring: {FRONTEND_URL}

Need help? Contact us at support@realdiag.org

Best regards,
The RealDiag Team
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .features {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .features ul {{ list-style: none; padding: 0; }}
        .features li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        .features li:before {{ content: "✓ "; color: #667eea; font-weight: bold; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 You're all set!</h1>
        </div>
        <div class="content">
            <p>Hi {full_name or 'there'},</p>
            
            <p>Your RealDiag employee account has been verified and is now active!</p>
            
            <div class="features">
                <h3>What you have access to:</h3>
                <ul>
                    <li>Unlimited diagnostic searches</li>
                    <li>All clinical modules</li>
                    <li>EHR integration</li>
                    <li>API access</li>
                    <li>Analytics dashboard</li>
                    <li>Priority support</li>
                </ul>
            </div>
            
            <p style="text-align: center;">
                <a href="{FRONTEND_URL}" class="button">Start Using RealDiag</a>
            </p>
            
            <p>Need help? Contact us at <a href="mailto:support@realdiag.org">support@realdiag.org</a></p>
        </div>
        <div class="footer">
            <p>© 2025 RealDiag. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach both versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Welcome email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        return False
