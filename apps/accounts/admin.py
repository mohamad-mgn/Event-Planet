"""
Admin configuration for Accounts app.

This module configures the Django admin interface for User and OTPCode models.
Provides a user-friendly interface for managing users and OTP codes.

Features:
- Custom user admin with phone number authentication
- OTP code management and monitoring
- User filtering and search
- Bulk actions for user management

Author: Event Planet Team
Created: 2026-02-15
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    
    Customizes the Django admin to work with our phone number-based
    authentication system instead of username-based.
    
    Features:
        - List view with phone number, name, role, verification status
        - Search by phone number, name, email
        - Filter by role, verification status, active status
        - Detailed view with organized fieldsets
        - Custom actions for bulk operations
    """
    
    # Fields to display in list view
    list_display = [
        'phone_number',
        'full_name',
        'email',
        'role',
        'is_verified_badge',
        'is_active',
        'created_at'
    ]
    
    # Filters in sidebar
    list_filter = [
        'role',
        'is_verified',
        'is_active',
        'is_staff',
        'created_at'
    ]
    
    # Search fields
    search_fields = [
        'phone_number',
        'full_name',
        'email'
    ]
    
    # Default ordering
    ordering = ['-created_at']
    
    # Read-only fields
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_login'
    ]
    
    # Fieldsets for detailed view
    fieldsets = (
        # Basic Information
        ('Basic Information', {
            'fields': (
                'phone_number',
                'full_name',
                'email'
            )
        }),
        
        # Role & Permissions
        ('Role & Permissions', {
            'fields': (
                'role',
                'is_verified',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
        
        # Timestamps
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'last_login'
            ),
            'classes': ('collapse',)  # Collapsed by default
        }),
        
        # Groups & Permissions (for superusers)
        ('Advanced', {
            'fields': (
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for creating new user
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'password1',
                'password2',
                'full_name',
                'email',
                'role',
                'is_verified',
                'is_active'
            ),
        }),
    )
    
    def is_verified_badge(self, obj):
        """
        Display verification status as a colored badge.
        
        Args:
            obj (User): User instance
        
        Returns:
            str: HTML badge showing verification status
        """
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✓ Verified</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✗ Not Verified</span>'
            )
    
    # Set column header for custom method
    is_verified_badge.short_description = 'Verification Status'
    
    # Custom admin actions
    actions = ['verify_users', 'make_organizers', 'make_participants']
    
    def verify_users(self, request, queryset):
        """
        Bulk action to verify selected users.
        
        Args:
            request: HTTP request
            queryset: Selected users
        """
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            f'{updated} user(s) were successfully verified.'
        )
    verify_users.short_description = 'Verify selected users'
    
    def make_organizers(self, request, queryset):
        """
        Bulk action to change role to organizer.
        
        Args:
            request: HTTP request
            queryset: Selected users
        """
        updated = queryset.update(role='organizer')
        self.message_user(
            request,
            f'{updated} user(s) changed to organizer role.'
        )
    make_organizers.short_description = 'Change role to Organizer'
    
    def make_participants(self, request, queryset):
        """
        Bulk action to change role to participant.
        
        Args:
            request: HTTP request
            queryset: Selected users
        """
        updated = queryset.update(role='participant')
        self.message_user(
            request,
            f'{updated} user(s) changed to participant role.'
        )
    make_participants.short_description = 'Change role to Participant'


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """
    Admin interface for OTPCode model.
    
    Provides monitoring and management of OTP codes.
    Useful for debugging authentication issues.
    
    Features:
        - List view with phone number, code, status
        - Search by phone number and code
        - Filter by usage status and expiration
        - Read-only view (OTPs shouldn't be modified)
    """
    
    # Fields to display in list view
    list_display = [
        'phone_number',
        'code',
        'status_badge',
        'expires_at',
        'created_at'
    ]
    
    # Filters in sidebar
    list_filter = [
        'is_used',
        'expires_at',
        'created_at'
    ]
    
    # Search fields
    search_fields = [
        'phone_number',
        'code'
    ]
    
    # Default ordering (newest first)
    ordering = ['-created_at']
    
    # Read-only fields (OTPs shouldn't be modified)
    readonly_fields = [
        'phone_number',
        'code',
        'expires_at',
        'is_used',
        'created_at',
        'updated_at'
    ]
    
    def status_badge(self, obj):
        """
        Display OTP status as a colored badge.
        
        Shows whether OTP is valid, used, or expired.
        
        Args:
            obj (OTPCode): OTPCode instance
        
        Returns:
            str: HTML badge showing OTP status
        """
        if obj.is_used:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Used</span>'
            )
        elif obj.is_expired:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Expired</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Valid</span>'
            )
    
    # Set column header
    status_badge.short_description = 'Status'
    
    # Disable add/edit capabilities (OTPs are created programmatically)
    def has_add_permission(self, request):
        """Disable manual OTP creation."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable OTP modification."""
        return False