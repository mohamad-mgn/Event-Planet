"""
Celery tasks for accounts app.
"""
from celery import shared_task
from django.utils import timezone


@shared_task
def cleanup_expired_otps():
    """
    Delete expired OTP codes from database.
    """
    from .models import OTPCode
    
    now = timezone.now()
    
    # Delete expired OTPs
    deleted_count, _ = OTPCode.objects.filter(
        expires_at__lt=now
    ).delete()
    
    print(f"🗑️ Cleaned up {deleted_count} expired OTP codes")
    return f"Deleted {deleted_count} expired OTPs"


@shared_task
def send_otp_sms(phone_number, otp_code):
    """
    Send OTP via SMS (background task).
    """
    print(f"📱 Sending OTP to {phone_number}: {otp_code}")
    
    # TODO: Integrate with SMS provider
    # Example with Kavenegar:
    # from kavenegar import KavenegarAPI
    # api = KavenegarAPI('YOUR_API_KEY')
    # api.sms_send({
    #     'receptor': phone_number,
    #     'message': f'Your OTP code is: {otp_code}'
    # })
    
    return f"OTP sent to {phone_number}"


@shared_task
def send_welcome_email(user_id):
    """
    Send welcome email to new user.
    """
    from .models import User
    
    try:
        user = User.objects.get(id=user_id)
        print(f"📧 Sending welcome email to {user.phone_number}")
        
        # TODO: Send actual email
        
        return f"Welcome email sent to {user.phone_number}"
    except User.DoesNotExist:
        return "User not found"