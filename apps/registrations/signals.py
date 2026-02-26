"""
Signals for the Registrations app.

This module contains signal handlers for registration-related events:
- Registration creation notifications
- Registration cancellation notifications
- Check-in notifications
- Capacity alerts

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Registration


@receiver(post_save, sender=Registration)
def registration_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when new registration is created.
    
    Notifies both participant and event organizer.
    
    Args:
        sender: The model class (Registration)
        instance: The actual Registration instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Send confirmation email to participant
        - Notify event organizer
        - Update event statistics
        - Check if event is full
    """
    if created:
        print(f"🎟️  New registration: {instance.participant.full_name} for {instance.event.title}")
        
        # Send confirmation email to participant
        # from apps.registrations.tasks import send_registration_confirmation
        # send_registration_confirmation.delay(instance.id)
        
        # Notify event organizer
        # from apps.registrations.tasks import notify_organizer_new_registration
        # notify_organizer_new_registration.delay(instance.id)
        
        # Check if event is now full
        if instance.event.is_full:
            print(f"🔴 Event is now full: {instance.event.title}")
            # from apps.events.tasks import notify_capacity_reached
            # notify_capacity_reached.delay(instance.event.id)


@receiver(post_save, sender=Registration)
def registration_confirmed_notification(sender, instance, created, **kwargs):
    """
    Send notification when registration is confirmed.
    
    Args:
        sender: The model class (Registration)
        instance: The actual Registration instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Send confirmation email
        - Add to calendar
        - Send event details
    """
    if not created and instance.status == 'confirmed':
        print(f"✅ Registration confirmed for {instance.participant.full_name}")
        
        # Send confirmation details
        # from apps.registrations.tasks import send_confirmation_details
        # send_confirmation_details.delay(instance.id)


@receiver(post_save, sender=Registration)
def registration_cancelled_notification(sender, instance, created, **kwargs):
    """
    Send notification when registration is cancelled.
    
    Args:
        sender: The model class (Registration)
        instance: The actual Registration instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Notify participant
        - Notify organizer
        - Free up capacity slot
        - Process refunds (if applicable)
    """
    if not created and instance.status == 'cancelled':
        print(f"❌ Registration cancelled: {instance.participant.full_name} for {instance.event.title}")
        
        # Send cancellation confirmation
        # from apps.registrations.tasks import send_cancellation_confirmation
        # send_cancellation_confirmation.delay(instance.id)
        
        # Notify organizer
        # from apps.registrations.tasks import notify_organizer_cancellation
        # notify_organizer_cancellation.delay(instance.id)


@receiver(post_save, sender=Registration)
def check_in_notification(sender, instance, created, **kwargs):
    """
    Send notification when participant checks in.
    
    Args:
        sender: The model class (Registration)
        instance: The actual Registration instance
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    
    Actions:
        - Log check-in time
        - Update attendance statistics
        - Send welcome message
    """
    if not created and instance.checked_in:
        print(f"✓ Participant checked in: {instance.participant.full_name}")
        
        # Could trigger welcome SMS or push notification
        # from apps.registrations.tasks import send_welcome_message
        # send_welcome_message.delay(instance.id)


@receiver(post_delete, sender=Registration)
def registration_deleted_notification(sender, instance, **kwargs):
    """
    Handle registration deletion.
    
    Args:
        sender: The model class (Registration)
        instance: The actual Registration instance being deleted
        **kwargs: Additional keyword arguments
    
    Actions:
        - Log deletion
        - Free up capacity
        - Update statistics
    """
    print(f"🗑️  Registration deleted: {instance.participant.full_name} for {instance.event.title}")


@receiver(pre_save, sender=Registration)
def track_registration_changes(sender, instance, **kwargs):
    """
    Track changes to registration fields.
    
    Args:
        sender: The model class (Registration)
        instance: The actual Registration instance being saved
        **kwargs: Additional keyword arguments
    
    Actions:
        - Log status changes
        - Track check-in changes
        - Audit trail
    """
    if instance.pk:
        try:
            old_registration = Registration.objects.get(pk=instance.pk)
            
            # Track status changes
            if old_registration.status != instance.status:
                print(f"🔄 Registration status changed: {old_registration.status} -> {instance.status}")
            
            # Track check-in changes
            if not old_registration.checked_in and instance.checked_in:
                print(f"✓ Check-in recorded for {instance.participant.full_name}")
        
        except Registration.DoesNotExist:
            pass