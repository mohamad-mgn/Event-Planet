"""
Views for the Accounts app.

This module contains API views for user authentication and management:
- SendOTPView: Send OTP to phone number
- VerifyOTPView: Verify OTP and login/register
- ProfileView: Get and update user profile
- ChangeRoleView: Change user role

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models import User
from .serializers import (
    UserSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ChangeRoleSerializer
)


class SendOTPView(generics.CreateAPIView):
    """
    API view to send OTP to phone number.
    
    This view generates a random OTP code and sends it to the provided
    phone number. The OTP is valid for 5 minutes.
    
    Endpoint: POST /api/accounts/auth/send-otp/
    
    Request Body:
        {
            "phone_number": "+989123456789"
        }
    
    Response (Success - 201):
        {
            "success": true,
            "message": "OTP sent successfully",
            "data": {
                "phone_number": "+989123456789",
                "otp": "123456"  // Only in development
            }
        }
    
    Response (Error - 400):
        {
            "success": false,
            "error": {
                "message": "Validation failed",
                "details": {
                    "phone_number": ["This field is required."]
                }
            }
        }
    
    Permissions:
        - AllowAny: No authentication required
    
    Rate Limiting:
        Consider adding rate limiting to prevent abuse
        (e.g., max 3 OTP requests per phone number per hour)
    """
    
    # Use SendOTPSerializer for validation and OTP generation
    serializer_class = SendOTPSerializer
    
    # No authentication required for sending OTP
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Handle OTP generation and sending.
        
        Args:
            request: HTTP request object
        
        Returns:
            Response: Success response with OTP data
        """
        # Validate request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate and send OTP
        result = serializer.save()
        
        # Return success response
        return Response({
            'success': True,
            'message': result['message'],
            'data': {
                'phone_number': str(result['phone_number']),
                'otp': result['otp']  # REMOVE IN PRODUCTION
            }
        }, status=status.HTTP_201_CREATED)


class VerifyOTPView(generics.CreateAPIView):
    """
    API view to verify OTP and login/register user.
    
    This view verifies the OTP code and either:
    - Creates a new user account (registration)
    - Logs in existing user
    
    Returns JWT tokens for authentication.
    
    Endpoint: POST /api/accounts/auth/verify-otp/
    
    Request Body:
        {
            "phone_number": "+989123456789",
            "otp": "123456",
            "full_name": "John Doe",  // Optional
            "email": "john@example.com",  // Optional
            "role": "participant"  // Optional (default: participant)
        }
    
    Response (Success - 201):
        {
            "success": true,
            "message": "Registration successful" or "Login successful",
            "data": {
                "user": {
                    "id": 1,
                    "phone_number": "+989123456789",
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "role": "participant",
                    "is_verified": true
                },
                "tokens": {
                    "refresh": "eyJ0eXAiOiJKV1QiLC...",
                    "access": "eyJ0eXAiOiJKV1QiLC..."
                }
            }
        }
    
    Response (Error - 400):
        {
            "success": false,
            "error": {
                "message": "Verification failed",
                "details": {
                    "otp": ["Invalid or expired OTP code."]
                }
            }
        }
    
    Permissions:
        - AllowAny: No authentication required
    """
    
    # Use VerifyOTPSerializer for validation and user creation
    serializer_class = VerifyOTPSerializer
    
    # No authentication required for OTP verification
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Handle OTP verification and user authentication.
        
        Args:
            request: HTTP request object
        
        Returns:
            Response: Success response with user data and tokens
        """
        # Validate request data and OTP
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify OTP and create/get user
        result = serializer.save()
        
        # Prepare user data for response
        user_serializer = UserSerializer(result['user'])
        
        # Determine success message
        message = 'Registration successful' if result['created'] else 'Login successful'
        
        # Return success response
        return Response({
            'success': True,
            'message': message,
            'data': {
                'user': user_serializer.data,
                'tokens': result['tokens']
            }
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API view to get and update user profile.
    
    Allows authenticated users to view and update their profile information.
    
    Endpoints:
        GET /api/accounts/profile/ - Get current user profile
        PUT /api/accounts/profile/ - Update full profile
        PATCH /api/accounts/profile/ - Partial profile update
    
    GET Response (200):
        {
            "success": true,
            "data": {
                "id": 1,
                "phone_number": "+989123456789",
                "full_name": "John Doe",
                "email": "john@example.com",
                "role": "participant",
                "is_verified": true,
                "created_at": "2026-02-15T10:30:00Z"
            }
        }
    
    PATCH Request Body:
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        }
    
    PATCH Response (200):
        {
            "success": true,
            "message": "Profile updated successfully",
            "data": {
                "id": 1,
                "phone_number": "+989123456789",
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                ...
            }
        }
    
    Permissions:
        - IsAuthenticated: User must be logged in
    """
    
    # Use UserSerializer for serialization
    serializer_class = UserSerializer
    
    # Require authentication
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """
        Get the current authenticated user.
        
        Returns:
            User: Current user instance
        """
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get user profile.
        
        Args:
            request: HTTP request object
        
        Returns:
            Response: User profile data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """
        Update user profile.
        
        Args:
            request: HTTP request object
        
        Returns:
            Response: Updated user profile data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': serializer.data
        })


class ChangeRoleView(APIView):
    """
    API view to change user role.
    
    Allows authenticated users to switch between participant and organizer roles.
    
    Endpoint: POST /api/accounts/change-role/
    
    Request Body:
        {
            "role": "organizer"
        }
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Role changed successfully",
            "data": {
                "id": 1,
                "phone_number": "+989123456789",
                "full_name": "John Doe",
                "role": "organizer",
                ...
            }
        }
    
    Response (Error - 400):
        {
            "success": false,
            "error": {
                "message": "Validation failed",
                "details": {
                    "role": ["Invalid role choice."]
                }
            }
        }
    
    Permissions:
        - IsAuthenticated: User must be logged in
    
    Note:
        Consider adding additional verification for role changes,
        such as admin approval or identity verification for organizers.
    """
    
    # Require authentication
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Handle role change request.
        
        Args:
            request: HTTP request object
        
        Returns:
            Response: Updated user data with new role
        """
        # Get current user
        user = request.user
        
        # Validate and update role
        serializer = ChangeRoleSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated user data
        user_serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'message': 'Role changed successfully',
            'data': user_serializer.data
        })