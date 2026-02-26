"""
URL configuration for Accounts app.

This module defines the URL patterns for user authentication
and profile management endpoints.

Endpoints:
    - POST /auth/send-otp/ - Send OTP to phone number
    - POST /auth/verify-otp/ - Verify OTP and login/register
    - GET/PUT/PATCH /profile/ - View and update user profile
    - POST /change-role/ - Change user role

Author: Event Planet Team
Created: 2026-02-15
"""

from django.urls import path
from .views import (
    SendOTPView,
    VerifyOTPView,
    ProfileView,
    ChangeRoleView
)

# App namespace for URL reversing
app_name = 'accounts'

urlpatterns = [
    # ----------------------------------------------------------------------
    # Authentication endpoints
    # ----------------------------------------------------------------------
    
    # Send OTP to phone number
    # POST /api/accounts/auth/send-otp/
    # Public endpoint - no authentication required
    path(
        'auth/send-otp/',
        SendOTPView.as_view(),
        name='send-otp'
    ),
    
    # Verify OTP and login/register
    # POST /api/accounts/auth/verify-otp/
    # Public endpoint - no authentication required
    path(
        'auth/verify-otp/',
        VerifyOTPView.as_view(),
        name='verify-otp'
    ),
    
    # ----------------------------------------------------------------------
    # Profile endpoints
    # ----------------------------------------------------------------------
    
    # Get and update user profile
    # GET /api/accounts/profile/ - Get profile
    # PUT /api/accounts/profile/ - Full update
    # PATCH /api/accounts/profile/ - Partial update
    # Protected endpoint - authentication required
    path(
        'profile/',
        ProfileView.as_view(),
        name='profile'
    ),
    
    # ----------------------------------------------------------------------
    # Role management endpoints
    # ----------------------------------------------------------------------
    
    # Change user role
    # POST /api/accounts/change-role/
    # Protected endpoint - authentication required
    path(
        'change-role/',
        ChangeRoleView.as_view(),
        name='change-role'
    ),
]