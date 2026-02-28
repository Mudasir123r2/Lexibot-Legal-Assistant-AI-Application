import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings

def create_transport():
    """Create SMTP connection"""
    print(f"🔌 Connecting to SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    smtp = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
    if not settings.SMTP_SECURE:
        smtp.starttls()
    smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
    print("✅ SMTP connection established")
    return smtp

async def send_reset_email(to: str, reset_url: str):
    """Send password reset email"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Reset your LexiBot password'
    msg['From'] = settings.MAIL_FROM.strip('"')
    msg['To'] = to
    
    html = f"""
    <div style="font-family:system-ui,sans-serif">
        <h2>Reset your password</h2>
        <p>Click the link below to set a new password. This link expires soon.</p>
        <p><a href="{reset_url}" style="background:#4f46e5;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none">Reset Password</a></p>
        <p>If you did not request this change, please ignore this email.</p>
    </div>
    """
    
    part = MIMEText(html, 'html')
    msg.attach(part)
    
    try:
        smtp = create_transport()
        smtp.sendmail(settings.MAIL_FROM.strip('"'), to, msg.as_string())
        smtp.quit()
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        raise

async def send_verification_email(to: str, verification_url: str):
    """Send email verification email"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Verify your LexiBot account'
    msg['From'] = settings.MAIL_FROM.strip('"')
    msg['To'] = to
    
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:600px;margin:0 auto">
        <h2 style="color:#4f46e5">Welcome to LexiBot!</h2>
        <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
        <p style="margin:20px 0">
            <a href="{verification_url}" style="background:#4f46e5;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;display:inline-block">Verify Email Address</a>
        </p>
        <p style="color:#666;font-size:14px">This link will expire in 24 hours. If you did not create an account, please ignore this email.</p>
    </div>
    """
    
    part = MIMEText(html, 'html')
    msg.attach(part)
    
    try:
        smtp = create_transport()
        smtp.sendmail(settings.MAIL_FROM.strip('"'), to, msg.as_string())
        smtp.quit()
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        raise
