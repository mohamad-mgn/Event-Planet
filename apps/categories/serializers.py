"""
Serializers for the Categories app.

This module contains serializers for category data:
- CategorySerializer: Full category details with event count
- CategoryListSerializer: Minimal category data for listings

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Full serializer for Category model.
    
    Includes all category fields plus computed event count.
    Used for detailed category views and admin operations.
    
    Fields:
        - id: Category ID (read-only)
        - name: Category name
        - slug: URL-friendly slug (read-only)
        - icon: Category icon/emoji
        - description: Category description
        - is_active: Active status
        - events_count: Number of events in category (read-only)
        - created_at: Creation timestamp (read-only)
        - updated_at: Last update timestamp (read-only)
    
    Example Response:
        {
            "id": 1,
            "name": "Technology & Science",
            "slug": "technology-science",
            "icon": "💻",
            "description": "Tech events, conferences, hackathons",
            "is_active": true,
            "events_count": 42,
            "created_at": "2026-02-15T10:00:00Z",
            "updated_at": "2026-02-15T10:00:00Z"
        }
    """
    
    # Include events count as a read-only field
    events_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'icon',
            'description',
            'is_active',
            'events_count',
            'created_at',
            'updated_at'
        ]
        # Read-only fields that cannot be modified via API
        read_only_fields = [
            'id',
            'slug',
            'events_count',
            'created_at',
            'updated_at'
        ]
    
    def get_events_count(self, obj):
        """
        Get number of published events in category.
        
        This method can be customized to change how events are counted
        (e.g., include only upcoming events, exclude archived events).
        
        Args:
            obj (Category): Category instance
        
        Returns:
            int: Number of published events
        """
        return obj.events_count


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for category listings.
    
    Used for dropdown lists, filters, and when full details aren't needed.
    Provides only essential fields for performance.
    
    Fields:
        - id: Category ID
        - name: Category name
        - slug: URL-friendly slug
        - icon: Category icon/emoji
        - events_count: Number of events (read-only)
    
    Example Response:
        {
            "id": 1,
            "name": "Technology & Science",
            "slug": "technology-science",
            "icon": "💻",
            "events_count": 42
        }
    
    Usage:
        GET /api/categories/ - Returns list of categories
        Used in event filtering and category selection dropdowns
    """
    
    # Include events count
    events_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'icon',
            'events_count'
        ]
        read_only_fields = ['id', 'slug', 'events_count']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single category view.
    
    Includes additional statistics and related data.
    Used for category detail pages.
    
    Fields:
        - All fields from CategorySerializer
        - active_events_count: Number of upcoming/active events
        - popular_events: List of popular events in category
    """
    
    # Statistics fields
    events_count = serializers.IntegerField(read_only=True)
    active_events_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'icon',
            'description',
            'is_active',
            'events_count',
            'active_events_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'slug',
            'events_count',
            'active_events_count',
            'created_at',
            'updated_at'
        ]
    
    def get_active_events_count(self, obj):
        """
        Get number of active (upcoming) events.
        
        Args:
            obj (Category): Category instance
        
        Returns:
            int: Number of active events
        """
        return obj.active_events_count