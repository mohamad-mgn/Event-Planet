"""
Celery tasks for the Accounts app.

This module contains asynchronous tasks for user-related operations:
- Send OTP via SMS
- Send welcome emails
- Clean up expired OTP codes
- User verification workflows

Tasks are executed asynchronously by Celery workers.

Author: Event Planet Team
Created: 2026-02-15
"""

from celery import shared_task
from django.utils import timezone
from .models import User, OTPCode


@shared_task
def cleanup_expired_otps():
    """
    Delete expired OTP codes from database.
    
    This task runs periodically (every 30 minutes) to clean up
    expired OTP codes and keep the database clean.
    
    Returns:
        int: Number of OTP codes deleted
    
    Schedule:
        Configured in config/celery.py to run every 30 minutes
    
    Example:
        # Manual execution
        from apps.accounts.tasks import cleanup_expired_otps
        cleanup_expired_otps.delay()
    
    Note:
        Only deletes OTP codes that have expired, not all OTPs.
        Keeps recent OTPs for audit purposes.
    """
    # Get current time
    now = timezone.now()
    
    # Find and delete expired OTPs
    deleted_count, _ = OTPCode.objects.filter(
        expires_at__lt=now  # Expiration time is in the past
    ).delete()
    
    # Log cleanup results
    print(f"🧹 Cleaned up {deleted_count} expired OTP codes")
    
    return deleted_count


@shared_task
def send_otp_sms(phone_number, otp_code):
    """
    Send OTP code via SMS.
    
    This task sends the OTP code to the user's phone number
    using an SMS service provider.
    
    Args:
        phone_number (str): Phone number to send OTP to
        otp_code (str): The OTP code to send
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    
    Example:
        # Queue SMS sending
        from apps.accounts.tasks import send_otp_sms
        send_otp_sms.delay('+989123456789', '123456')
    
    SMS Providers:
        - Twilio: https://www.twilio.com/
        - Kavenegar (Iran): https://kavenegar.com/
        - AWS SNS: https://aws.amazon.com/sns/
        - Vonage: https://www.vonage.com/
    
    Note:
        This is a placeholder. Implement actual SMS sending logic
        based on your SMS service provider.
    """
    # TODO: Implement actual SMS sending
    # Example using Twilio:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     body=f"Your Event Planet verification code is: {otp_code}",
    #     from_='+1234567890',
    #     to=phone_number
    # )
    
    # For now, just log to console
    print(f"📱 SMS sent to {phone_number}: Your OTP code is {otp_code}")
    
    return True


@shared_task
def send_welcome_email(user_id):
    """
    Send welcome email to new user.
    
    This task sends a welcome email to users when they register.
    Includes information about getting started with the platform.
    
    Args:
        user_id (int): ID of the user to send email to
    
    Returns:
        bool: True if email sent successfully, False otherwise
    
    Example:
        # Queue welcome email
        from apps.accounts.tasks import send_welcome_email
        send_welcome_email.delay(1)
    
    Note:
        Only sends email if user has an email address.
        Template can be customized in templates/emails/welcome.html
    """
    try:
        # Get user from database
        user = User.objects.get(id=user_id)
        
        # Check if user has email
        if not user.email:
            print(f"⚠️  User {user.phone_number} has no email address")
            return False
        
        # TODO: Implement actual email sending
        # Example using Django's send_mail:
        # from django.core.mail import send_mail
        # from django.template.loader import render_to_string
        # 
        # subject = 'Welcome to Event Planet!'
        # html_message = render_to_string('emails/welcome.html', {
        #     'user': user,
        # })
        # 
        # send_mail(
        #     subject=subject,
        #     message='',
        #     from_email='noreply@eventplanet.com',
        #     recipient_list=[user.email],
        #     html_message=html_message,
        # )
        
        # For now, just log to console
        print(f"📧 Welcome email sent to {user.email}")
        
        return True
        
    except User.DoesNotExist:
        print(f"❌ User with ID {user_id} does not exist")
        return False


@shared_task
def send_verification_reminder(user_id):
    """
    Send reminder to unverified users.
    
    This task sends a reminder to users who haven't verified
    their phone number within a certain time period.
    
    Args:
        user_id (int): ID of the user to send reminder to
    
    Returns:
        bool: True if reminder sent, False otherwise
    
    Schedule:
        Could be configured to run daily and check for unverified users
        created more than 24 hours ago.
    
    Example:
        # Queue verification reminder
        from apps.accounts.tasks import send_verification_reminder
        send_verification_reminder.delay(1)
    """
    try:
        # Get user from database
        user = User.objects.get(id=user_id)
        
        # Only send reminder if user is not verified
        if user.is_verified:
            return False
        
        # TODO: Implement reminder sending logic
        # - Send SMS reminder
        # - Send email reminder (if available)
        # - Send push notification
        
        print(f"🔔 Verification reminder sent to {user.phone_number}")
        
        return True
        
    except User.DoesNotExist:
        return False


@shared_task
def deactivate_inactive_users():
    """
    Deactivate users who haven't logged in for a long time.
    
    This task finds users who haven't logged in for a specified
    period (e.g., 6 months) and deactivates their accounts.
    
    Returns:
        int: Number of users deactivated
    
    Schedule:
        Could be configured to run monthly
    
    Note:
        Deactivated users can reactivate by logging in again.
        Consider sending warning email before deactivation.
    """
    from datetime import timedelta
    
    # Define inactivity threshold (e.g., 180 days)
    threshold = timezone.now() - timedelta(days=180)
    
    # Find inactive users
    inactive_users = User.objects.filter(
        last_login__lt=threshold,
        is_active=True
    )
    
    # Deactivate users
    count = inactive_users.update(is_active=False)
    
    print(f"🔒 Deactivated {count} inactive users")
    
    return count