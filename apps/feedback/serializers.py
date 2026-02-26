"""
Serializers for the Feedback app.

This module contains serializers for feedback management:
- FeedbackSerializer: Full feedback details
- FeedbackCreateSerializer: Feedback creation
- FeedbackListSerializer: Minimal feedback data
- OrganizerResponseSerializer: Organizer response handling

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import serializers
from .models import Feedback
from apps.accounts.serializers import UserSerializer
from apps.events.serializers import EventListSerializer


class FeedbackSerializer(serializers.ModelSerializer):
    """
    Full serializer for Feedback model.
    
    Includes all feedback details with related participant data.
    """
    
    participant = UserSerializer(read_only=True)
    event = EventListSerializer(read_only=True)
    
    # Computed fields
    rating_stars = serializers.CharField(read_only=True)
    has_response = serializers.BooleanField(read_only=True)
    is_positive = serializers.BooleanField(read_only=True)
    is_negative = serializers.BooleanField(read_only=True)
    is_neutral = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id',
            'event',
            'participant',
            'rating',
            'rating_stars',
            'review',
            'organizer_response',
            'is_published',
            'has_response',
            'is_positive',
            'is_negative',
            'is_neutral',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'participant',
            'organizer_response',
            'rating_stars',
            'has_response',
            'is_positive',
            'is_negative',
            'is_neutral',
            'created_at',
            'updated_at'
        ]


class FeedbackListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for feedback listings.
    
    Used for list views where full details aren't needed.
    """
    
    participant_name = serializers.CharField(
        source='participant.full_name',
        read_only=True
    )
    event_title = serializers.CharField(
        source='event.title',
        read_only=True
    )
    rating_stars = serializers.CharField(read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id',
            'event_title',
            'participant_name',
            'rating',
            'rating_stars',
            'review',
            'has_response',
            'created_at'
        ]


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating feedback.
    
    Validates feedback data and handles creation logic.
    Participant is set automatically from request user.
    """
    
    event_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'event_id',
            'rating',
            'review'
        ]
    
    def validate_event_id(self, value):
        """
        Validate event exists.
        
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
        
        return value
    
    def validate_rating(self, value):
        """
        Validate rating is between 1 and 5.
        
        Args:
            value: Rating value
        
        Returns:
            int: Validated rating
        
        Raises:
            ValidationError: If rating invalid
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Rating must be between 1 and 5.'
            )
        
        return value
    
    def validate(self, attrs):
        """
        Validate feedback data.
        
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
                'participant': 'Only participants can provide feedback.'
            })
        
        # Check if participant registered for event
        from apps.registrations.models import Registration
        
        if not Registration.objects.filter(
            event_id=event_id,
            participant=participant,
            status='confirmed'
        ).exists():
            raise serializers.ValidationError({
                'event': 'You must have registered for this event to provide feedback.'
            })
        
        # Check for duplicate feedback
        if Feedback.objects.filter(
            event_id=event_id,
            participant=participant
        ).exists():
            raise serializers.ValidationError({
                'event': 'You have already provided feedback for this event.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create feedback.
        
        Args:
            validated_data: Validated serializer data
        
        Returns:
            Feedback: Created feedback instance
        """
        event_id = validated_data.pop('event_id')
        participant = self.context['request'].user
        
        feedback = Feedback.objects.create(
            event_id=event_id,
            participant=participant,
            **validated_data
        )
        
        return feedback


class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating feedback.
    
    Allows participants to update their rating and review.
    """
    
    class Meta:
        model = Feedback
        fields = [
            'rating',
            'review',
            'is_published'
        ]
    
    def validate_rating(self, value):
        """Validate rating."""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Rating must be between 1 and 5.'
            )
        return value


class OrganizerResponseSerializer(serializers.Serializer):
    """
    Serializer for organizer response to feedback.
    
    Allows event organizers to respond to participant feedback.
    """
    
    organizer_response = serializers.CharField(
        max_length=1000,
        required=True
    )
    
    def validate_organizer_response(self, value):
        """
        Validate response text.
        
        Args:
            value: Response text
        
        Returns:
            str: Validated response
        
        Raises:
            ValidationError: If response is empty or too short
        """
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                'Response must be at least 10 characters long.'
            )
        
        return value
    
    def update(self, instance, validated_data):
        """
        Add organizer response.
        
        Args:
            instance: Feedback instance
            validated_data: Validated data
        
        Returns:
            Feedback: Updated feedback
        """
        response = validated_data.get('organizer_response')
        instance.respond(response)
        return instance