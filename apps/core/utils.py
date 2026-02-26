"""
Utility functions for Event Planet project.

This module contains helper functions used across the project:
- OTP generation and verification
- Phone number formatting
- Date/time utilities
- String manipulation helpers

Author: Event Planet Team
Created: 2026-02-15
"""

import random
import string
from django.core.cache import cache
from django.conf import settings


def generate_otp(length=6):
    """
    Generate a random numeric OTP (One-Time Password) code.
    
    The OTP consists of random digits and is used for phone number
    verification during user registration and login.
    
    Args:
        length (int): Length of the OTP code (default: 6)
    
    Returns:
        str: Random OTP code consisting of digits
    
    Examples:
        >>> generate_otp()
        '123456'
        
        >>> generate_otp(length=4)
        '5678'
    
    Note:
        The OTP is purely numeric to make it easy for users to type
        from SMS messages.
    """
    return ''.join(random.choices(string.digits, k=length))


def store_otp(phone_number, otp):
    """
    Store OTP code in cache with expiration time.
    
    The OTP is stored in Redis cache with a TTL (Time To Live) based
    on the OTP_EXPIRY_TIME setting. After expiration, the OTP is
    automatically deleted.
    
    Args:
        phone_number (str): Phone number to associate with OTP
        otp (str): The OTP code to store
    
    Returns:
        bool: Always returns True
    
    Cache Key Format:
        otp_{phone_number}
    
    Example:
        >>> store_otp('+989123456789', '123456')
        True
    
    Note:
        This function is kept for backward compatibility but is no longer
        actively used. OTP verification now uses database storage via
        OTPCode model for better reliability.
    """
    cache_key = f'otp_{phone_number}'
    cache.set(cache_key, otp, timeout=settings.OTP_EXPIRY_TIME)
    return True


def verify_otp(phone_number, otp):
    """
    Verify OTP code from cache.
    
    Checks if the provided OTP matches the one stored in cache for
    the given phone number. If verification succeeds, the OTP is
    deleted from cache.
    
    Args:
        phone_number (str): Phone number to verify
        otp (str): OTP code to verify
    
    Returns:
        bool: True if OTP is valid and matches, False otherwise
    
    Example:
        >>> verify_otp('+989123456789', '123456')
        True  # If OTP matches
        
        >>> verify_otp('+989123456789', '999999')
        False  # If OTP doesn't match or expired
    
    Note:
        This function is kept for backward compatibility but is no longer
        actively used. OTP verification now uses database storage via
        OTPCode model for better reliability.
    """
    cache_key = f'otp_{phone_number}'
    stored_otp = cache.get(cache_key)
    
    # Check if OTP exists and matches
    if stored_otp and stored_otp == otp:
        # Delete OTP after successful verification (one-time use)
        cache.delete(cache_key)
        return True
    
    return False


def get_otp_remaining_time(phone_number):
    """
    Get remaining validity time for an OTP.
    
    Returns the number of seconds remaining before the OTP expires.
    Useful for showing countdown timers to users.
    
    Args:
        phone_number (str): Phone number to check
    
    Returns:
        int: Remaining seconds until expiration, or 0 if expired/not found
    
    Example:
        >>> get_otp_remaining_time('+989123456789')
        245  # OTP expires in 245 seconds
    
    Note:
        This function requires Redis cache backend that supports TTL queries.
        Will return 0 if the cache backend doesn't support TTL.
    """
    cache_key = f'otp_{phone_number}'
    
    try:
        # Try to get TTL (Time To Live) from cache
        ttl = cache.ttl(cache_key)
        return ttl if ttl and ttl > 0 else 0
    except AttributeError:
        # If cache backend doesn't support TTL, return 0
        return 0


def format_phone_number(phone_number):
    """
    Format phone number to international format.
    
    Ensures phone numbers are consistently formatted in international
    format (E.164 standard) for storage and display.
    
    Args:
        phone_number (str or PhoneNumber): Phone number to format
    
    Returns:
        str: Formatted phone number in international format
    
    Examples:
        >>> format_phone_number('09123456789')
        '+989123456789'
        
        >>> format_phone_number('+98 912 345 6789')
        '+989123456789'
    
    Note:
        Uses phonenumber_field library for proper formatting.
        Assumes Iranian numbers if country code is not provided.
    """
    from phonenumber_field.phonenumber import PhoneNumber
    
    # If already a PhoneNumber object, just convert to string
    if isinstance(phone_number, PhoneNumber):
        return str(phone_number)
    
    # Parse and format the phone number
    try:
        phone = PhoneNumber.from_string(
            phone_number,
            region=settings.PHONENUMBER_DEFAULT_REGION
        )
        return str(phone)
    except Exception:
        # If parsing fails, return original number
        return phone_number


def generate_slug(text, max_length=50):
    """
    Generate a URL-friendly slug from text.
    
    Converts text to lowercase, removes special characters,
    and replaces spaces with hyphens.
    
    Args:
        text (str): Text to convert to slug
        max_length (int): Maximum length of slug (default: 50)
    
    Returns:
        str: URL-friendly slug
    
    Examples:
        >>> generate_slug('Hello World!')
        'hello-world'
        
        >>> generate_slug('Event @ 2026', max_length=10)
        'event-2026'
    
    Note:
        For production use, consider using django.utils.text.slugify
        which handles Unicode characters better.
    """
    from django.utils.text import slugify
    
    # Use Django's slugify utility for proper Unicode handling
    slug = slugify(text)
    
    # Truncate to max length
    return slug[:max_length]