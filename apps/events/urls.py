"""
URL configuration for Events app.

This module defines URL patterns for event management endpoints.

Endpoints:
    - GET /api/events/public/ - List published events
    - GET /api/events/{slug}/ - Get event details
    - POST /api/events/create/ - Create new event
    - PUT/PATCH /api/events/{id}/update/ - Update event
    - DELETE /api/events/{id}/delete/ - Delete event
    - GET /api/events/my-events/ - List user's events
    - POST /api/events/{id}/publish/ - Publish event
    - POST /api/events/{id}/close/ - Close event registration

Author: Event Planet Team
Created: 2026-02-15
"""

from django.urls import path
from .views import (
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    MyEventsView,
    EventPublishView,
    EventCloseView
)

# App namespace for URL reversing
app_name = 'events'

urlpatterns = [
    # ----------------------------------------------------------------------
    # Public event endpoints
    # ----------------------------------------------------------------------
    
    # List all published events (with filters)
    # GET /api/events/public/
    # Public endpoint - no authentication required
    # Query params: ?category=1&search=tech&is_online=true&upcoming=true
    path(
        'public/',
        EventListView.as_view(),
        name='event-list'
    ),
    
    # Get single event details
    # GET /api/events/{slug}/
    # Public endpoint - no authentication required
    # Increments view count
    path(
        '<slug:slug>/',
        EventDetailView.as_view(),
        name='event-detail'
    ),
    
    # ----------------------------------------------------------------------
    # Event management endpoints (Organizers only)
    # ----------------------------------------------------------------------
    
    # Create new event
    # POST /api/events/create/
    # Protected endpoint - organizer authentication required
    path(
        'create/',
        EventCreateView.as_view(),
        name='event-create'
    ),
    
    # Update event
    # PUT /api/events/{id}/update/
    # PATCH /api/events/{id}/update/
    # Protected endpoint - event owner only
    path(
        '<int:pk>/update/',
        EventUpdateView.as_view(),
        name='event-update'
    ),
    
    # Delete event (draft only)
    # DELETE /api/events/{id}/delete/
    # Protected endpoint - event owner only
    path(
        '<int:pk>/delete/',
        EventDeleteView.as_view(),
        name='event-delete'
    ),
    
    # List user's organized events
    # GET /api/events/my-events/
    # Protected endpoint - organizer authentication required
    path(
        'my-events/',
        MyEventsView.as_view(),
        name='my-events'
    ),
    
    # ----------------------------------------------------------------------
    # Event status management endpoints
    # ----------------------------------------------------------------------
    
    # Publish event (draft -> published)
    # POST /api/events/{id}/publish/
    # Protected endpoint - event owner only
    path(
        '<int:pk>/publish/',
        EventPublishView.as_view(),
        name='event-publish'
    ),
    
    # Close event registration (published -> closed)
    # POST /api/events/{id}/close/
    # Protected endpoint - event owner only
    path(
        '<int:pk>/close/',
        EventCloseView.as_view(),
        name='event-close'
    ),
]