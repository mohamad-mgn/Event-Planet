"""
Serializers for the Registrations app.

This module contains serializers for registration management:
- RegistrationSerializer: Full registration details
- RegistrationCreateSerializer: Registration creation
- RegistrationListSerializer: Minimal registration data
- CheckInSerializer: Check-in handling

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Registration
from apps.events.serializers import EventListSerializer
from apps.accounts.serializers import UserSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Full serializer for Registration model.
    
    Includes all registration details with related event and participant data.
    """
    
    event = EventListSerializer(read_only=True)
    participant = UserSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    # Computed fields
    is_confirmed = serializers.BooleanField(read_only=True)
    is_cancelled = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    can_check_in = serializers.BooleanField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Registration
        fields = [
            'id',
            'event',
            'participant',
            'status',
            'status_display',
            'notes',
            'checked_in',
            'checked_in_at',
            'cancelled_at',
            'cancellation_reason',
            'is_confirmed',
            'is_cancelled',
            'is_pending',
            'can_check_in',
            'can_cancel',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'participant',
            'checked_in',
            'checked_in_at',
            'cancelled_at',
            'is_confirmed',
            'is_cancelled',
            'is_pending',
            'can_check_in',
            'can_cancel',
            'created_at',
            'updated_at'
        ]


class RegistrationListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for registration listings.
    
    Used for list views where full details aren't needed.
    """
    
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_start = serializers.DateTimeField(
        source='event.start_datetime',
        read_only=True
    )
    participant_name = serializers.CharField(
        source='participant.full_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Registration
        fields = [
            'id',
            'event_title',
            'event_start',
            'participant_name',
            'status',
            'status_display',
            'checked_in',
            'created_at'
        ]


class RegistrationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating registrations.
    
    Validates registration data and handles creation logic.
    Participant is set automatically from request user.
    """
    
    event_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Registration
        fields = [
            'event_id',
            'notes'
        ]
    
    def validate_event_id(self, value):
        """
        Validate event exists and is accepting registrations.
        
        Args:
            value: Event ID
        
        Returns:
            int: Validated event ID
        
        Raises:
            ValidationError: If event invalid
        """
        from apps.events.models import Event
        
        try:
            event = Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError('Event does not exist.')
        
        # Check event status
        if event.status not in ['published', 'closed']:
            raise serializers.ValidationError(
                'Event is not accepting registrations.'
            )
        
        # Check if event is full
        if event.is_full:
            raise serializers.ValidationError(
                'Event is full. No more registrations accepted.'
            )
        
        # Check if event is in the past
        if event.is_past:
            raise serializers.ValidationError(
                'Cannot register for past events.'
            )
        
        return value
    
    def validate(self, attrs):
        """
        Validate registration data.
        
        Args:
            attrs: Validated field data
        
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If validation fails
        """
        participant = self.context['request'].user
        event_id = attrs.get('event_id')
        
        # Check participant role
        if participant.role != 'participant':
            raise serializers.ValidationError({
                'participant': 'Only users with participant role can register.'
            })
        
        # Check for duplicate registration
        if Registration.objects.filter(
            event_id=event_id,
            participant=participant
        ).exists():
            raise serializers.ValidationError({
                'event': 'You are already registered for this event.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create registration.
        
        Args:
            validated_data: Validated serializer data
        
        Returns:
            Registration: Created registration instance
        """
        event_id = validated_data.pop('event_id')
        participant = self.context['request'].user
        
        registration = Registration.objects.create(
            event_id=event_id,
            participant=participant,
            status='confirmed',
            **validated_data
        )
        
        return registration


class CancelRegistrationSerializer(serializers.Serializer):
    """
    Serializer for cancelling registration.
    
    Handles registration cancellation with optional reason.
    """
    
    cancellation_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    def validate(self, attrs):
        """
        Validate cancellation.
        
        Args:
            attrs: Field data
        
        Returns:
            dict: Validated data
        """
        registration = self.instance
        
        if not registration.can_cancel:
            raise serializers.ValidationError(
                'This registration cannot be cancelled.'
            )
        
        return attrs
    
    def update(self, instance, validated_data):
        """
        Cancel registration.
        
        Args:
            instance: Registration instance
            validated_data: Validated data
        
        Returns:
            Registration: Updated registration
        """
        reason = validated_data.get('cancellation_reason', '')
        instance.cancel(reason=reason)
        return instance


class CheckInSerializer(serializers.Serializer):
    """
    Serializer for checking in participants.
    
    Used by organizers to mark participants as checked in.
    """
    
    def validate(self, attrs):
        """
        Validate check-in.
        
        Args:
            attrs: Field data
        
        Returns:
            dict: Validated data
        """
        registration = self.instance
        
        if not registration.can_check_in:
            raise serializers.ValidationError(
                'Participant cannot check in at this time.'
            )
        
        return attrs
    
    def update(self, instance, validated_data):
        """
        Check in participant.
        
        Args:
            instance: Registration instance
            validated_data: Validated data
        
        Returns:
            Registration: Updated registration
        """
        success = instance.check_in_participant()
        
        if not success:
            raise serializers.ValidationError(
                'Check-in failed.'
            )
        
        return instance