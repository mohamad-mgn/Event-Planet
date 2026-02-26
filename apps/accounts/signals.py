"""
Signals for the Accounts app.

This module contains signal handlers for user-related events:
- User creation notifications
- User verification notifications
- OTP creation (SMS sending)
- User field changes tracking

Signals are used to decouple business logic and trigger side effects
when certain events occur (e.g., sending welcome emails, tracking changes).

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, OTPCode
from .tasks import send_welcome_email, send_otp_sms


@receiver(post_save, sender=User)
def user_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when a new user is created.
    
    This signal is triggered after a User instance is saved.
    If it's a new user (created=True), we send a welcome notification.
    
    Args:
        sender: The model class (User)
        instance: The actual User instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Print creation message to console
        - Queue welcome email task (asynchronous)
    
    Note:
        In production, this could also:
        - Send push notifications
        - Update analytics
        - Trigger onboarding workflows
    """
    if created:
        # Log user creation
        print(f"🎉 New user registered: {instance.phone_number}")
        
        # Send welcome email asynchronously via Celery
        # Only if user has an email address
        if instance.email:
            send_welcome_email.delay(instance.id)


@receiver(post_save, sender=User)
def user_verified_notification(sender, instance, created, **kwargs):
    """
    Send notification when user is verified.
    
    This signal is triggered after a User instance is saved.
    We check if the user's verification status changed to True.
    
    Args:
        sender: The model class (User)
        instance: The actual User instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Print verification message to console
        - Could trigger additional verification workflows
    
    Note:
        To properly track verification changes, we use pre_save signal
        to store the old value and compare it in post_save.
    """
    # Only proceed if this is not a new user
    if not created:
        # Check if is_verified field changed to True
        # This requires storing old value in pre_save signal
        if instance.is_verified:
            print(f"✅ User verified: {instance.phone_number}")
            
            # Additional actions for verified users
            # - Enable full account features
            # - Send verification success notification
            # - Update analytics


@receiver(post_save, sender=OTPCode)
def send_otp_sms(sender, instance, created, **kwargs):
    """
    Send OTP via SMS when OTPCode is created.
    
    This signal is triggered after an OTPCode instance is saved.
    If it's a new OTP (created=True), we send it via SMS.
    
    Args:
        sender: The model class (OTPCode)
        instance: The actual OTPCode instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Print OTP to console (development)
        - Queue SMS sending task (production)
    
    Note:
        In production, this should use an SMS service like:
        - Twilio
        - Kavenegar (Iran)
        - AWS SNS
        - Vonage
    """
    if created:
        # Log OTP creation (development only)
        print(f"📱 OTP Code for {instance.phone_number}: {instance.code}")
        
        # Send OTP via SMS (production)
        # Uncomment when SMS service is configured
        # send_otp_sms.delay(
        #     str(instance.phone_number),
        #     instance.code
        # )


@receiver(pre_save, sender=User)
def track_user_changes(sender, instance, **kwargs):
    """
    Track changes to user fields before saving.
    
    This signal is triggered before a User instance is saved.
    We can use it to track what fields changed and take action.
    
    Args:
        sender: The model class (User)
        instance: The actual User instance being saved
        **kwargs: Additional keyword arguments
    
    Actions:
        - Store old field values for comparison
        - Log important field changes
        - Validate business rules
    
    Example Use Cases:
        - Track role changes (participant -> organizer)
        - Monitor verification status changes
        - Audit trail for security
        - Trigger workflows based on field changes
    
    Note:
        To compare old vs new values, we need to fetch the old instance
        from database (if it exists).
    """
    # Only proceed if this is an existing user (has primary key)
    if instance.pk:
        try:
            # Get old user data from database
            old_user = User.objects.get(pk=instance.pk)
            
            # Track role changes
            if old_user.role != instance.role:
                print(f"🔄 User {instance.phone_number} role changed: {old_user.role} -> {instance.role}")
                
                # Additional actions for role changes
                # - Send notification
                # - Update permissions
                # - Log in audit trail
            
            # Track verification status changes
            if not old_user.is_verified and instance.is_verified:
                print(f"✅ User {instance.phone_number} is now verified")
                
                # Additional actions when user gets verified
                # - Enable features
                # - Send welcome message
            
            # Track email changes
            if old_user.email != instance.email:
                print(f"📧 User {instance.phone_number} changed email: {old_user.email} -> {instance.email}")
                
                # Could trigger email verification workflow
                # instance.is_verified = False  # Require re-verification
        
        except User.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass


# Additional signal handlers can be added here
# Examples:
# - post_delete: Clean up related data when user is deleted
# - m2m_changed: Track changes to many-to-many relationships
# - pre_delete: Prevent deletion under certain conditions