"""
URL configuration for Registrations app.

This module defines URL patterns for registration management endpoints.

Endpoints:
    - POST /api/registrations/create/ - Create new registration
    - GET /api/registrations/my-registrations/ - List user's registrations
    - GET /api/registrations/{id}/ - Get registration details
    - POST /api/registrations/{id}/cancel/ - Cancel registration
    - POST /api/registrations/{id}/check-in/ - Check in participant

Author: Event Planet Team
Created: 2026-02-15
"""

from django.urls import path
from .views import (
    RegistrationCreateView,
    MyRegistrationsView,
    RegistrationDetailView,
    CancelRegistrationView,
    CheckInView
)

# App namespace for URL reversing
app_name = 'registrations'

urlpatterns = [
    # ----------------------------------------------------------------------
    # Registration creation endpoint
    # ----------------------------------------------------------------------
    
    # Create new registration
    # POST /api/registrations/create/
    # Protected endpoint - participant authentication required
    path(
        'create/',
        RegistrationCreateView.as_view(),
        name='registration-create'
    ),
    
    # ----------------------------------------------------------------------
    # User registrations endpoints
    # ----------------------------------------------------------------------
    
    # List user's registrations
    # GET /api/registrations/my-registrations/
    # Protected endpoint - participant authentication required
    # Query params: ?status=confirmed&upcoming=true
    path(
        'my-registrations/',
        MyRegistrationsView.as_view(),
        name='my-registrations'
    ),
    
    # Get single registration details
    # GET /api/registrations/{id}/
    # Protected endpoint - participant (owner) only
    path(
        '<int:pk>/',
        RegistrationDetailView.as_view(),
        name='registration-detail'
    ),
    
    # ----------------------------------------------------------------------
    # Registration management endpoints
    # ----------------------------------------------------------------------
    
    # Cancel registration
    # POST /api/registrations/{id}/cancel/
    # Protected endpoint - participant (owner) only
    path(
        '<int:pk>/cancel/',
        CancelRegistrationView.as_view(),
        name='registration-cancel'
    ),
    
    # Check in participant
    # POST /api/registrations/{id}/check-in/
    # Protected endpoint - event organizer only
    path(
        '<int:pk>/check-in/',
        CheckInView.as_view(),
        name='registration-checkin'
    ),
]