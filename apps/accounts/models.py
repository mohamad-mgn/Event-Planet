"""
Models for the Accounts app.

This module defines the user authentication and OTP verification models:
- User: Custom user model with phone number authentication
- OTPCode: One-time password codes for phone verification

The User model supports two roles:
- participant: Can register for events and provide feedback
- organizer: Can create and manage events

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    
    Provides helper methods for creating users and superusers.
    Handles phone number-based authentication instead of username.
    """
    
    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and save a regular user with the given phone number.
        
        Args:
            phone_number (str): User's phone number (used for authentication)
            password (str, optional): User's password
            **extra_fields: Additional fields (full_name, email, role, etc.)
        
        Returns:
            User: Created user instance
        
        Raises:
            ValueError: If phone_number is not provided
        
        Example:
            >>> user = User.objects.create_user(
            ...     phone_number='+989123456789',
            ...     password='secure_password',
            ...     full_name='John Doe',
            ...     role='participant'
            ... )
        """
        # Validate phone number is provided
        if not phone_number:
            raise ValueError('Phone number is required')
        
        # Create user instance
        user = self.model(phone_number=phone_number, **extra_fields)
        
        # Set password (hashed automatically)
        if password:
            user.set_password(password)
        
        # Save to database
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Create and save a superuser with admin privileges.
        
        Superusers have access to the Django admin panel and all permissions.
        
        Args:
            phone_number (str): Superuser's phone number
            password (str): Superuser's password
            **extra_fields: Additional fields
        
        Returns:
            User: Created superuser instance
        
        Example:
            >>> admin = User.objects.create_superuser(
            ...     phone_number='+989123456789',
            ...     password='admin_password',
            ...     full_name='Admin User'
            ... )
        """
        # Set superuser flags
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        # Ensure superuser flags are set correctly
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        # Create superuser using create_user method
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User model for Event Planet.
    
    Uses phone number as the unique identifier instead of username.
    Supports two roles: participant and organizer.
    
    Fields:
        phone_number: Unique phone number (used for authentication)
        full_name: User's full name
        email: Optional email address
        role: User role (participant or organizer)
        is_verified: Whether phone number is verified
        is_active: Whether user account is active
        is_staff: Whether user can access admin panel
        last_login: Timestamp of last login
    
    Inherited from TimeStampedModel:
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    # Role choices for users
    ROLE_CHOICES = [
        ('participant', 'Participant'),  # Can register for events
        ('organizer', 'Organizer'),      # Can create and manage events
    ]
    
    # Phone number field (unique identifier for authentication)
    # Uses phonenumber_field for international phone number validation
    phone_number = PhoneNumberField(
        unique=True,
        verbose_name='Phone Number',
        help_text='User phone number in international format (e.g., +989123456789)'
    )
    
    # User's full name
    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Full Name',
        help_text='User full name'
    )
    
    # Optional email address
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email Address',
        help_text='User email address (optional)'
    )
    
    # User role (determines permissions)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='participant',
        verbose_name='Role',
        help_text='User role in the system'
    )
    
    # Verification status (whether phone number is verified via OTP)
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Verified',
        help_text='Whether phone number has been verified'
    )
    
    # Account activation status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Whether user account is active'
    )
    
    # Staff status (for admin panel access)
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff Status',
        help_text='Whether user can access admin panel'
    )
    
    # Custom manager
    objects = UserManager()
    
    # Use phone_number for authentication instead of username
    USERNAME_FIELD = 'phone_number'
    
    # Required fields when creating superuser
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),  # Index for faster lookups
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        """
        String representation of user.
        
        Returns:
            str: User's phone number
        """
        return str(self.phone_number)
    
    def get_full_name(self):
        """
        Get user's full name.
        
        Returns:
            str: User's full name or phone number if name not set
        """
        return self.full_name or str(self.phone_number)
    
    def get_short_name(self):
        """
        Get user's short name.
        
        Returns:
            str: First part of full name or phone number
        """
        if self.full_name:
            return self.full_name.split()[0]
        return str(self.phone_number)
    
    @property
    def is_organizer(self):
        """
        Check if user is an organizer.
        
        Returns:
            bool: True if user role is 'organizer'
        """
        return self.role == 'organizer'
    
    @property
    def is_participant(self):
        """
        Check if user is a participant.
        
        Returns:
            bool: True if user role is 'participant'
        """
        return self.role == 'participant'


class OTPCode(TimeStampedModel):
    """
    OTP (One-Time Password) model for phone verification.
    
    Stores OTP codes sent to users for phone number verification
    during registration and login. Each OTP has an expiration time
    and can only be used once.
    
    Fields:
        phone_number: Phone number the OTP was sent to
        code: 6-digit OTP code
        expires_at: Expiration timestamp
        is_used: Whether OTP has been used
    
    Inherited from TimeStampedModel:
        created_at: OTP creation timestamp
        updated_at: Last update timestamp
    """
    
    # Phone number the OTP was sent to
    phone_number = PhoneNumberField(
        verbose_name='Phone Number',
        help_text='Phone number to verify'
    )
    
    # 6-digit OTP code
    code = models.CharField(
        max_length=6,
        verbose_name='OTP Code',
        help_text='6-digit verification code'
    )
    
    # Expiration timestamp (typically 5 minutes after creation)
    expires_at = models.DateTimeField(
        verbose_name='Expires At',
        help_text='Timestamp when OTP expires'
    )
    
    # Whether OTP has been used (one-time use only)
    is_used = models.BooleanField(
        default=False,
        verbose_name='Used',
        help_text='Whether OTP has been used for verification'
    )
    
    class Meta:
        verbose_name = 'OTP Code'
        verbose_name_plural = 'OTP Codes'
        ordering = ['-created_at']
        indexes = [
            # Composite index for efficient OTP lookups
            models.Index(fields=['phone_number', 'code', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        """
        String representation of OTP.
        
        Returns:
            str: Phone number and OTP code
        """
        return f"{self.phone_number} - {self.code}"
    
    def is_valid(self):
        """
        Check if OTP is still valid.
        
        An OTP is valid if:
        1. It hasn't been used yet
        2. It hasn't expired
        
        Returns:
            bool: True if OTP is valid, False otherwise
        """
        return (
            not self.is_used and
            timezone.now() < self.expires_at
        )
    
    def mark_as_used(self):
        """
        Mark OTP as used.
        
        Should be called after successful verification to prevent reuse.
        """
        self.is_used = True
        self.save(update_fields=['is_used'])
    
    @property
    def is_expired(self):
        """
        Check if OTP has expired.
        
        Returns:
            bool: True if OTP has expired
        """
        return timezone.now() >= self.expires_at