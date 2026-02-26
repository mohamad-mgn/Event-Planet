"""
Serializers for the Accounts app.

This module contains serializers for user authentication and management:
- UserSerializer: User data serialization
- SendOTPSerializer: OTP generation and sending
- VerifyOTPSerializer: OTP verification and user registration/login
- ChangeRoleSerializer: User role management

Author: Event Planet Team
Created: 2026-02-15
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, OTPCode
from apps.core.utils import generate_otp


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Provides read-only serialization of user data for API responses.
    Used in profile endpoints and user listing.
    
    Fields:
        - id: User ID (read-only)
        - phone_number: User's phone number
        - full_name: User's full name
        - email: User's email (optional)
        - role: User role (participant/organizer)
        - is_verified: Verification status
        - created_at: Account creation date (read-only)
    """
    
    # Use PhoneNumberField for proper phone number validation
    phone_number = PhoneNumberField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'full_name',
            'email',
            'role',
            'is_verified',
            'created_at'
        ]
        # Read-only fields that cannot be modified via API
        read_only_fields = ['id', 'is_verified', 'created_at']


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer for sending OTP to phone number.
    
    Handles OTP generation and storage for phone number verification.
    Creates an OTPCode record in the database with expiration time.
    
    Input:
        phone_number: Phone number to send OTP to
    
    Output:
        phone_number: Phone number OTP was sent to
        message: Success message
        otp: OTP code (only in development, remove in production)
    
    Usage:
        POST /api/accounts/auth/send-otp/
        {
            "phone_number": "+989123456789"
        }
    """
    
    # Phone number field with validation
    phone_number = PhoneNumberField()
    
    def validate_phone_number(self, value):
        """
        Validate phone number format.
        
        Args:
            value: Phone number to validate
        
        Returns:
            PhoneNumber: Validated phone number
        
        Raises:
            ValidationError: If phone number is invalid or empty
        """
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value
    
    def create(self, validated_data):
        """
        Generate and send OTP to phone number.
        
        This method:
        1. Generates a random 6-digit OTP
        2. Stores it in database with 5-minute expiration
        3. In production, would trigger SMS sending
        
        Args:
            validated_data: Validated serializer data
        
        Returns:
            dict: Response data with phone number and OTP
        
        Note:
            In production, the 'otp' field should be removed from response
            and OTP should be sent via SMS service instead.
        """
        phone_number = validated_data['phone_number']
        
        # Generate 6-digit OTP code
        otp_code = generate_otp()
        
        # Calculate expiration time (5 minutes from now)
        expires_at = timezone.now() + timedelta(seconds=300)
        
        # Store OTP in database
        OTPCode.objects.create(
            phone_number=phone_number,
            code=otp_code,
            expires_at=expires_at
        )
        
        # TODO: Send SMS here using SMS service (Twilio, Kavenegar, etc.)
        # For development, we print it to console
        print(f"🔐 OTP for {phone_number}: {otp_code}")
        
        return {
            'phone_number': phone_number,
            'message': 'OTP sent successfully',
            'otp': otp_code  # REMOVE THIS IN PRODUCTION!
        }


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying OTP and registering/logging in user.
    
    This serializer handles the complete authentication flow:
    1. Validates OTP code
    2. Creates new user or retrieves existing user
    3. Generates JWT tokens for authentication
    
    Input:
        phone_number: Phone number to verify
        otp: 6-digit OTP code
        full_name: User's full name (optional, for new users)
        email: User's email (optional)
        role: User role (participant/organizer, default: participant)
    
    Output:
        user: User object data
        tokens: JWT access and refresh tokens
        created: Whether a new user was created
    
    Usage:
        POST /api/accounts/auth/verify-otp/
        {
            "phone_number": "+989123456789",
            "otp": "123456",
            "full_name": "John Doe",
            "role": "participant"
        }
    """
    
    # Required fields
    phone_number = PhoneNumberField()
    otp = serializers.CharField(max_length=6, min_length=6)
    
    # Optional fields (for new users)
    full_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True
    )
    role = serializers.ChoiceField(
        choices=['participant', 'organizer'],
        default='participant',
        required=False
    )
    
    def validate(self, attrs):
        """
        Validate OTP code.
        
        Checks if OTP exists in database, hasn't been used,
        and hasn't expired.
        
        Args:
            attrs: Dictionary of field values
        
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If OTP is invalid or expired
        """
        phone_number = attrs.get('phone_number')
        otp = attrs.get('otp')
        
        # Check OTP in database
        try:
            otp_obj = OTPCode.objects.get(
                phone_number=phone_number,
                code=otp,
                is_used=False
            )
            
            # Check if OTP has expired
            if not otp_obj.is_valid():
                raise serializers.ValidationError({
                    'otp': 'OTP code has expired.'
                })
            
            # Mark OTP as used to prevent reuse
            otp_obj.is_used = True
            otp_obj.save()
            
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError({
                'otp': 'Invalid OTP code.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create or get user and return JWT tokens.
        
        This method:
        1. Gets existing user or creates new one
        2. Updates user information if provided
        3. Marks user as verified
        4. Generates JWT access and refresh tokens
        
        Args:
            validated_data: Validated serializer data
        
        Returns:
            dict: User object, tokens, and creation status
        """
        phone_number = validated_data['phone_number']
        full_name = validated_data.get('full_name', '')
        email = validated_data.get('email', '')
        role = validated_data.get('role', 'participant')
        
        # Get existing user or create new one
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'full_name': full_name,
                'email': email,
                'role': role,
                'is_verified': True
            }
        )
        
        # Update existing user information
        if not created:
            # Update fields if provided
            if full_name:
                user.full_name = full_name
            if email:
                user.email = email
            
            # Mark as verified and update last login
            user.is_verified = True
            user.last_login = timezone.now()
            user.save()
        
        # Generate JWT tokens for authentication
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'created': created
        }


class ChangeRoleSerializer(serializers.Serializer):
    """
    Serializer for changing user role.
    
    Allows users to switch between participant and organizer roles.
    This is useful when a participant wants to become an event organizer.
    
    Input:
        role: New role (participant or organizer)
    
    Usage:
        POST /api/accounts/change-role/
        {
            "role": "organizer"
        }
    
    Note:
        This endpoint should be protected with authentication.
        Consider adding additional verification for role changes
        (e.g., requiring admin approval for organizer role).
    """
    
    # Role field with validation
    role = serializers.ChoiceField(choices=['participant', 'organizer'])
    
    def update(self, instance, validated_data):
        """
        Update user role.
        
        Args:
            instance: User instance to update
            validated_data: Validated serializer data
        
        Returns:
            User: Updated user instance
        """
        # Update user role
        instance.role = validated_data['role']
        instance.save()
        
        return instance