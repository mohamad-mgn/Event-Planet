"""
Admin configuration for Feedback app.

This module configures the Django admin interface for Feedback model.

Features:
- List view with event, participant, rating, review
- Filtering by rating, published status, event
- Search by participant and event
- Bulk publish/unpublish actions
- Rating visualization
- Response management

Author: Event Planet Team
Created: 2026-02-15
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Admin interface for Feedback model.
    
    Provides comprehensive feedback management with:
    - List view with key information
    - Filtering by rating, status, event
    - Search by participant and event
    - Bulk actions for publication
    - Visual rating display
    """
    
    # Fields to display in list view
    list_display = [
        'get_participant_name',
        'get_event_title',
        'rating_display',
        'has_response_badge',
        'is_published_badge',
        'created_at'
    ]
    
    # Filters in sidebar
    list_filter = [
        'rating',
        'is_published',
        'created_at',
        'event'
    ]
    
    # Search fields
    search_fields = [
        'participant__phone_number',
        'participant__full_name',
        'event__title',
        'review',
        'organizer_response'
    ]
    
    # Default ordering (newest first)
    ordering = ['-created_at']
    
    # Read-only fields
    readonly_fields = [
        'created_at',
        'updated_at',
        'rating_stars'
    ]
    
    # Fieldsets for detailed view
    fieldsets = (
        # Basic Information
        ('Feedback Information', {
            'fields': (
                'event',
                'participant',
                'rating',
                'rating_stars',
                'review'
            )
        }),
        
        # Organizer Response
        ('Organizer Response', {
            'fields': (
                'organizer_response',
            )
        }),
        
        # Publication Status
        ('Publication', {
            'fields': (
                'is_published',
            )
        }),
        
        # Timestamps
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_participant_name(self, obj):
        """
        Display participant name with link.
        
        Args:
            obj (Feedback): Feedback instance
        
        Returns:
            str: HTML with participant name link
        """
        url = f'/admin/accounts/user/{obj.participant.id}/change/'
        return format_html(
            '<a href="{}" style="color: #007bff;">{}</a>',
            url,
            obj.participant.full_name or obj.participant.phone_number
        )
    
    get_participant_name.short_description = 'Participant'
    get_participant_name.admin_order_field = 'participant__full_name'
    
    def get_event_title(self, obj):
        """
        Display event title with link.
        
        Args:
            obj (Feedback): Feedback instance
        
        Returns:
            str: HTML with event title link
        """
        url = f'/admin/events/event/{obj.event.id}/change/'
        return format_html(
            '<a href="{}" style="color: #007bff;">{}</a>',
            url,
            obj.event.title
        )
    
    get_event_title.short_description = 'Event'
    get_event_title.admin_order_field = 'event__title'
    
    def rating_display(self, obj):
        """
        Display rating as stars with color.
        
        Args:
            obj (Feedback): Feedback instance
        
        Returns:
            str: HTML with star rating
        """
        colors = {
            5: '#28a745',  # Green
            4: '#17a2b8',  # Blue
            3: '#ffc107',  # Yellow
            2: '#fd7e14',  # Orange
            1: '#dc3545',  # Red
        }
        
        return format_html(
            '<span style="color: {}; font-size: 16px;">{}</span> <span style="color: #6c757d;">({}/5)</span>',
            colors.get(obj.rating, '#6c757d'),
            '⭐' * obj.rating,
            obj.rating
        )
    
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'
    
    def has_response_badge(self, obj):
        """
        Display if organizer has responded.
        
        Args:
            obj (Feedback): Feedback instance
        
        Returns:
            str: HTML badge showing response status
        """
        if obj.has_response:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✓ Responded</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 10px; border-radius: 3px;">No Response</span>'
            )
    
    has_response_badge.short_description = 'Response'
    
    def is_published_badge(self, obj):
        """
        Display publication status as badge.
        
        Args:
            obj (Feedback): Feedback instance
        
        Returns:
            str: HTML badge showing publication status
        """
        if obj.is_published:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✓ Published</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✗ Unpublished</span>'
            )
    
    is_published_badge.short_description = 'Status'
    
    def rating_stars(self, obj):
        """
        Display rating as stars for detail view.
        
        Args:
            obj (Feedback): Feedback instance
        
        Returns:
            str: Star string
        """
        return obj.rating_stars
    
    rating_stars.short_description = 'Rating (Stars)'
    
    # Custom admin actions
    actions = [
        'publish_feedbacks',
        'unpublish_feedbacks'
    ]
    
    def publish_feedbacks(self, request, queryset):
        """
        Bulk action to publish feedbacks.
        
        Args:
            request: HTTP request
            queryset: Selected feedbacks
        """
        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            f'{updated} feedback(s) published successfully.'
        )
    publish_feedbacks.short_description = 'Publish selected feedbacks'
    
    def unpublish_feedbacks(self, request, queryset):
        """
        Bulk action to unpublish feedbacks.
        
        Args:
            request: HTTP request
            queryset: Selected feedbacks
        """
        updated = queryset.update(is_published=False)
        self.message_user(
            request,
            f'{updated} feedback(s) unpublished successfully.'
        )
    unpublish_feedbacks.short_description = 'Unpublish selected feedbacks'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        
        Args:
            request: HTTP request
        
        Returns:
            QuerySet: Optimized queryset
        """
        queryset = super().get_queryset(request)
        
        # Use select_related for efficient queries
        queryset = queryset.select_related(
            'event',
            'participant'
        )
        
        return queryset