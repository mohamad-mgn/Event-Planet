"""
Custom permission classes for Event Planet API.

This module contains reusable permission classes that control access
to API endpoints based on user roles and ownership.

Permission classes:
- IsOwnerOrReadOnly: Only owners can modify, others can only read
- IsOrganizerOrReadOnly: Only organizers can modify, others can only read
- IsParticipant: Only participants have access
- IsOrganizer: Only organizers have access
- IsOwner: Only the owner has access

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read access to everyone,
    but write access only to the owner of the object.
    
    Usage:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsOwnerOrReadOnly]
    
    Behavior:
        - GET, HEAD, OPTIONS: Allowed for everyone
        - POST, PUT, PATCH, DELETE: Only allowed for the owner
    
    Note:
        The object must have an attribute that identifies the owner.
        By default, this checks if obj.user == request.user
        Override get_owner() to use a different attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the request should be permitted for the specific object.
        
        Args:
            request: The incoming request
            view: The view being accessed
            obj: The object being accessed
        
        Returns:
            bool: True if permission granted, False otherwise
        """
        # Read permissions are allowed for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        # Check if object has 'user' attribute and it matches the request user
        return hasattr(obj, 'user') and obj.user == request.user


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read access to everyone,
    but write access only to users with 'organizer' role.
    
    Usage:
        class EventViewSet(viewsets.ModelViewSet):
            permission_classes = [IsOrganizerOrReadOnly]
    
    Behavior:
        - GET, HEAD, OPTIONS: Allowed for everyone
        - POST, PUT, PATCH, DELETE: Only allowed for organizers
    """
    
    def has_permission(self, request, view):
        """
        Check if the request should be permitted at the view level.
        
        Args:
            request: The incoming request
            view: The view being accessed
        
        Returns:
            bool: True if permission granted, False otherwise
        """
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication and organizer role
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'organizer'
        )


class IsParticipant(permissions.BasePermission):
    """
    Permission class that only allows access to users with 'participant' role.
    
    Usage:
        class RegistrationViewSet(viewsets.ModelViewSet):
            permission_classes = [IsParticipant]
    
    Behavior:
        - All methods: Only allowed for authenticated users with 'participant' role
    """
    
    def has_permission(self, request, view):
        """
        Check if the request should be permitted.
        
        Args:
            request: The incoming request
            view: The view being accessed
        
        Returns:
            bool: True if user is authenticated and is a participant
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'participant'
        )


class IsOrganizer(permissions.BasePermission):
    """
    Permission class that only allows access to users with 'organizer' role.
    
    Usage:
        class EventCreateView(viewsets.ModelViewSet):
            permission_classes = [IsOrganizer]
    
    Behavior:
        - All methods: Only allowed for authenticated users with 'organizer' role
    """
    
    def has_permission(self, request, view):
        """
        Check if the request should be permitted.
        
        Args:
            request: The incoming request
            view: The view being accessed
        
        Returns:
            bool: True if user is authenticated and is an organizer
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'organizer'
        )


class IsOwner(permissions.BasePermission):
    """
    Permission class that only allows access to the owner of the object.
    
    Usage:
        class ProfileViewSet(viewsets.ModelViewSet):
            permission_classes = [IsOwner]
    
    Behavior:
        - All methods: Only allowed if the object belongs to the requesting user
    
    Note:
        The object must have an attribute that identifies the owner.
        By default, this checks if obj.user == request.user
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the request should be permitted for the specific object.
        
        Args:
            request: The incoming request
            view: The view being accessed
            obj: The object being accessed
        
        Returns:
            bool: True if object belongs to the requesting user
        """
        # Check if object has 'user' attribute and it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If object is the user itself (e.g., User profile)
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsEventOrganizer(permissions.BasePermission):
    """
    Permission class that only allows access to the organizer of the event.
    
    Usage:
        class EventUpdateView(viewsets.ModelViewSet):
            permission_classes = [IsEventOrganizer]
    
    Behavior:
        - All methods: Only allowed if the user is the organizer of the event
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the request should be permitted for the specific event.
        
        Args:
            request: The incoming request
            view: The view being accessed
            obj: The event object being accessed
        
        Returns:
            bool: True if user is the organizer of the event
        """
        # Check if object is an event and has 'organizer' attribute
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        
        # If object is related to an event (e.g., EventStage, Registration)
        if hasattr(obj, 'event') and hasattr(obj.event, 'organizer'):
            return obj.event.organizer == request.user
        
        return False