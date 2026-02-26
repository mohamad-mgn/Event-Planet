"""
Core abstract models for Event Planet project.

This module contains abstract base models that provide common functionality
for all other models in the project. These models are not created as database
tables but are inherited by other models.

Features:
- TimeStampedModel: Automatic created_at and updated_at timestamps
- SoftDeleteModel: Soft delete functionality (mark as deleted instead of removing)
- PublishableModel: Publishing workflow with draft/published/archived states

Author: Event Planet Team
Created: 2026-02-15
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides automatic timestamp fields.
    
    This model adds two fields to any model that inherits from it:
    - created_at: Automatically set when the object is created
    - updated_at: Automatically updated whenever the object is saved
    
    Usage:
        class MyModel(TimeStampedModel):
            name = models.CharField(max_length=100)
            # created_at and updated_at are automatically included
    """
    
    # Timestamp when the record was created
    # auto_now_add: Automatically set to now when object is first created
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    
    # Timestamp when the record was last updated
    # auto_now: Automatically set to now every time the object is saved
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )
    
    class Meta:
        # This is an abstract model (no database table will be created)
        abstract = True
        
        # Default ordering by creation time (newest first)
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    
    Instead of permanently deleting records from the database,
    this model marks them as deleted by setting is_deleted=True
    and deleted_at timestamp.
    
    Benefits:
    - Records can be recovered if needed
    - Maintains data integrity and audit trail
    - Related records are not orphaned
    
    Usage:
        class MyModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
            # Soft delete
            obj.delete()  # Sets is_deleted=True
            
            # Permanent delete (if needed)
            obj.delete(force=True)
    """
    
    # Flag to indicate if the record is deleted
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,  # Index for faster queries
        help_text="Whether the record has been soft deleted"
    )
    
    # Timestamp when the record was soft deleted
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the record was soft deleted"
    )
    
    class Meta:
        # This is an abstract model
        abstract = True
    
    def delete(self, using=None, keep_parents=False, force=False):
        """
        Override delete method to implement soft delete.
        
        Args:
            using: Database alias to use
            keep_parents: Keep parent records (for model inheritance)
            force: If True, permanently delete the record
        
        Returns:
            Tuple of (number_deleted, dict_of_deletions) if force=True
            None if soft delete (force=False)
        """
        if force:
            # Permanently delete the record from database
            return super().delete(using=using, keep_parents=keep_parents)
        else:
            # Soft delete: Mark as deleted
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(using=using)
    
    def restore(self):
        """
        Restore a soft-deleted record.
        
        Sets is_deleted back to False and clears deleted_at timestamp.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class PublishableModel(models.Model):
    """
    Abstract base model for content that goes through a publishing workflow.
    
    This model provides three states:
    - draft: Content is being created/edited (not visible to public)
    - published: Content is live and visible to public
    - archived: Content is no longer active but preserved
    
    Usage:
        class Article(PublishableModel):
            title = models.CharField(max_length=200)
            content = models.TextField()
            
            # Publishing workflow
            article.publish()   # Changes status to 'published'
            article.unpublish() # Changes status to 'draft'
            article.archive()   # Changes status to 'archived'
    """
    
    # Status choices for publishing workflow
    STATUS_CHOICES = [
        ('draft', 'Draft'),           # Being created/edited
        ('published', 'Published'),   # Live and public
        ('archived', 'Archived'),     # No longer active
    ]
    
    # Current publishing status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,  # Index for faster filtering
        help_text="Current publishing status of the content"
    )
    
    # Timestamp when content was published
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the content was published"
    )
    
    class Meta:
        # This is an abstract model
        abstract = True
    
    def publish(self):
        """
        Publish the content (make it public).
        
        Changes status to 'published' and sets published_at timestamp
        if it hasn't been set before.
        """
        self.status = 'published'
        if not self.published_at:
            self.published_at = timezone.now()
        self.save()
    
    def unpublish(self):
        """
        Unpublish the content (make it draft).
        
        Changes status back to 'draft' without clearing published_at.
        This preserves the original publication date if re-published.
        """
        self.status = 'draft'
        self.save()
    
    def archive(self):
        """
        Archive the content.
        
        Changes status to 'archived'. Archived content is preserved
        but no longer actively used.
        """
        self.status = 'archived'
        self.save()
    
    @property
    def is_published(self):
        """
        Check if content is currently published.
        
        Returns:
            bool: True if status is 'published', False otherwise
        """
        return self.status == 'published'
    
    @property
    def is_draft(self):
        """
        Check if content is in draft state.
        
        Returns:
            bool: True if status is 'draft', False otherwise
        """
        return self.status == 'draft'
    
    @property
    def is_archived(self):
        """
        Check if content is archived.
        
        Returns:
            bool: True if status is 'archived', False otherwise
        """
        return self.status == 'archived'