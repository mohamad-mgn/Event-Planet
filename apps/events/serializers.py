"""
Serializers for the Events app.

This module contains serializers for event management:
- EventSerializer: Full event details
- EventListSerializer: Minimal event data for listings
- EventCreateSerializer: Event creation
- EventStageSerializer: Event stage details
- StageRoleSerializer: Stage role details
- EventResultSerializer: Event result details

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    Event,
    EventStage,
    StageRole,
    AttributeDefinition,
    EventAttributeValue,
    EventResult
)
from apps.categories.serializers import CategoryListSerializer
from apps.accounts.serializers import UserSerializer


class StageRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for StageRole model.
    
    Used for displaying speakers, hosts, and other people
    involved in event stages.
    """
    
    role_type_display = serializers.CharField(
        source='get_role_type_display',
        read_only=True
    )
    
    class Meta:
        model = StageRole
        fields = [
            'id',
            'role_type',
            'role_type_display',
            'name',
            'bio',
            'profile_image'
        ]


class EventStageSerializer(serializers.ModelSerializer):
    """
    Serializer for EventStage model.
    
    Includes stage details and related roles (speakers, hosts, etc.).
    """
    
    roles = StageRoleSerializer(many=True, read_only=True)
    
    class Meta:
        model = EventStage
        fields = [
            'id',
            'order',
            'title',
            'description',
            'start_datetime',
            'end_datetime',
            'location',
            'capacity',
            'roles',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EventAttributeValueSerializer(serializers.ModelSerializer):
    """
    Serializer for EventAttributeValue model.
    
    Handles dynamic attributes using EAV pattern.
    """
    
    attribute_name = serializers.CharField(
        source='attribute.name',
        read_only=True
    )
    
    attribute_display_name = serializers.CharField(
        source='attribute.display_name',
        read_only=True
    )
    
    value = serializers.SerializerMethodField()
    
    class Meta:
        model = EventAttributeValue
        fields = [
            'id',
            'attribute_name',
            'attribute_display_name',
            'value'
        ]
    
    def get_value(self, obj):
        """Get the appropriate value based on data type."""
        return obj.get_value()


class EventResultSerializer(serializers.ModelSerializer):
    """
    Serializer for EventResult model.
    
    Used for displaying event results and announcements.
    """
    
    class Meta:
        model = EventResult
        fields = [
            'id',
            'title',
            'content',
            'attachment',
            'published_at'
        ]
        read_only_fields = ['id', 'published_at']


class EventListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for event listings.
    
    Used for list views where full details aren't needed.
    Optimized for performance.
    """
    
    category = CategoryListSerializer(read_only=True)
    organizer_name = serializers.CharField(
        source='organizer.full_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'category',
            'organizer_name',
            'start_datetime',
            'end_datetime',
            'location',
            'is_online',
            'capacity',
            'status',
            'status_display',
            'cover_image',
            'views_count',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'slug',
            'views_count',
            'created_at'
        ]


class EventSerializer(serializers.ModelSerializer):
    """
    Full serializer for Event model.
    
    Includes all event details, related stages, attributes, and computed fields.
    Used for detail views and event management.
    """
    
    # Related fields
    category = CategoryListSerializer(read_only=True)
    organizer = UserSerializer(read_only=True)
    stages = EventStageSerializer(many=True, read_only=True)
    attribute_values = EventAttributeValueSerializer(many=True, read_only=True)
    results = EventResultSerializer(many=True, read_only=True)
    
    # Display fields
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    # Computed fields
    registration_count = serializers.IntegerField(read_only=True)
    confirmed_registrations_count = serializers.IntegerField(read_only=True)
    available_slots = serializers.SerializerMethodField()
    is_full = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    duration_hours = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'organizer',
            'category',
            'start_datetime',
            'end_datetime',
            'location',
            'is_online',
            'online_link',
            'capacity',
            'status',
            'status_display',
            'cover_image',
            'views_count',
            'registration_count',
            'confirmed_registrations_count',
            'available_slots',
            'is_full',
            'is_upcoming',
            'is_ongoing',
            'is_past',
            'duration_hours',
            'stages',
            'attribute_values',
            'results',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'slug',
            'organizer',
            'views_count',
            'registration_count',
            'confirmed_registrations_count',
            'available_slots',
            'is_full',
            'is_upcoming',
            'is_ongoing',
            'is_past',
            'duration_hours',
            'created_at',
            'updated_at'
        ]
    
    def get_available_slots(self, obj):
        """Get available slots as string or number."""
        slots = obj.available_slots
        return slots if isinstance(slots, str) else int(slots)


class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating events.
    
    Validates event data and handles creation logic.
    Organizer is set automatically from request user.
    """
    
    # Accept category ID instead of full object
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'category_id',
            'start_datetime',
            'end_datetime',
            'location',
            'is_online',
            'online_link',
            'capacity',
            'cover_image'
        ]
    
    def validate(self, attrs):
        """
        Validate event data.
        
        Checks:
        - End datetime is after start datetime
        - Online events have online link
        - Start datetime is in the future
        """
        start = attrs.get('start_datetime')
        end = attrs.get('end_datetime')
        
        # Validate datetime order
        if end <= start:
            raise serializers.ValidationError({
                'end_datetime': 'End datetime must be after start datetime.'
            })
        
        # Validate start is in future
        if start <= timezone.now():
            raise serializers.ValidationError({
                'start_datetime': 'Event must start in the future.'
            })
        
        # Validate online event has link
        if attrs.get('is_online') and not attrs.get('online_link'):
            raise serializers.ValidationError({
                'online_link': 'Online link is required for online events.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create event with organizer from request.
        
        Args:
            validated_data: Validated serializer data
        
        Returns:
            Event: Created event instance
        """
        # Get category ID and remove from validated_data
        category_id = validated_data.pop('category_id')
        
        # Get organizer from request context
        organizer = self.context['request'].user
        
        # Create event
        event = Event.objects.create(
            organizer=organizer,
            category_id=category_id,
            **validated_data
        )
        
        return event


class EventUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating events.
    
    Allows updating most fields except organizer and slug.
    """
    
    category_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'category_id',
            'start_datetime',
            'end_datetime',
            'location',
            'is_online',
            'online_link',
            'capacity',
            'status',
            'cover_image'
        ]
    
    def validate(self, attrs):
        """Validate update data."""
        instance = self.instance
        
        # Get datetime values (use existing if not provided)
        start = attrs.get('start_datetime', instance.start_datetime)
        end = attrs.get('end_datetime', instance.end_datetime)
        
        # Validate datetime order
        if end <= start:
            raise serializers.ValidationError({
                'end_datetime': 'End datetime must be after start datetime.'
            })
        
        # Validate status transition
        new_status = attrs.get('status')
        if new_status and new_status != instance.status:
            if not instance.can_transition_to(new_status):
                raise serializers.ValidationError({
                    'status': f'Cannot transition from {instance.status} to {new_status}.'
                })
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update event instance."""
        # Handle category_id if provided
        category_id = validated_data.pop('category_id', None)
        if category_id:
            instance.category_id = category_id
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance