"""
URL configuration for Feedback app.

This module defines URL patterns for feedback management endpoints.

Endpoints:
    - POST /api/feedback/create/ - Create new feedback
    - GET /api/feedback/event/{event_id}/ - List event feedbacks
    - GET /api/feedback/event/{event_id}/stats/ - Event feedback statistics
    - GET /api/feedback/my-feedbacks/ - List user's feedbacks
    - GET /api/feedback/{id}/ - Get feedback details
    - PUT/PATCH /api/feedback/{id}/update/ - Update feedback
    - DELETE /api/feedback/{id}/delete/ - Delete feedback
    - POST /api/feedback/{id}/respond/ - Add organizer response

Author: Event Planet Team
Created: 2026-02-15
"""

from django.urls import path
from .views import (
    FeedbackCreateView,
    FeedbackListView,
    MyFeedbacksView,
    FeedbackDetailView,
    FeedbackUpdateView,
    FeedbackDeleteView,
    OrganizerResponseView,
    EventFeedbackStatsView
)

# App namespace for URL reversing
app_name = 'feedback'

urlpatterns = [
    # ----------------------------------------------------------------------
    # Feedback creation endpoint
    # ----------------------------------------------------------------------
    
    # Create new feedback
    # POST /api/feedback/create/
    # Protected endpoint - participant authentication required
    path(
        'create/',
        FeedbackCreateView.as_view(),
        name='feedback-create'
    ),
    
    # ----------------------------------------------------------------------
    # Event feedback endpoints
    # ----------------------------------------------------------------------
    
    # List feedbacks for specific event
    # GET /api/feedback/event/{event_id}/
    # Public endpoint - no authentication required
    # Query params: ?rating=5&min_rating=4
    path(
        'event/<int:event_id>/',
        FeedbackListView.as_view(),
        name='event-feedbacks'
    ),
    
    # Get event feedback statistics
    # GET /api/feedback/event/{event_id}/stats/
    # Public endpoint - no authentication required
    path(
        'event/<int:event_id>/stats/',
        EventFeedbackStatsView.as_view(),
        name='event-feedback-stats'
    ),
    
    # ----------------------------------------------------------------------
    # User feedback endpoints
    # ----------------------------------------------------------------------
    
    # List user's feedbacks
    # GET /api/feedback/my-feedbacks/
    # Protected endpoint - participant authentication required
    path(
        'my-feedbacks/',
        MyFeedbacksView.as_view(),
        name='my-feedbacks'
    ),
    
    # Get single feedback details
    # GET /api/feedback/{id}/
    # Public endpoint (for published feedbacks)
    path(
        '<int:pk>/',
        FeedbackDetailView.as_view(),
        name='feedback-detail'
    ),
    
    # ----------------------------------------------------------------------
    # Feedback management endpoints
    # ----------------------------------------------------------------------
    
    # Update feedback
    # PUT /api/feedback/{id}/update/
    # PATCH /api/feedback/{id}/update/
    # Protected endpoint - participant (owner) only
    path(
        '<int:pk>/update/',
        FeedbackUpdateView.as_view(),
        name='feedback-update'
    ),
    
    # Delete feedback
    # DELETE /api/feedback/{id}/delete/
    # Protected endpoint - participant (owner) only
    path(
        '<int:pk>/delete/',
        FeedbackDeleteView.as_view(),
        name='feedback-delete'
    ),
    
    # ----------------------------------------------------------------------
    # Organizer response endpoint
    # ----------------------------------------------------------------------
    
    # Add organizer response to feedback
    # POST /api/feedback/{id}/respond/
    # Protected endpoint - event organizer only
    path(
        '<int:pk>/respond/',
        OrganizerResponseView.as_view(),
        name='feedback-respond'
    ),
]