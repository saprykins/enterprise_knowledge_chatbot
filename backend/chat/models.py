from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Model for storing chat conversations."""
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Conversation {self.id}"

    class Meta:
        ordering = ['-updated_at']


class Message(models.Model):
    """Model for storing individual chat messages."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

    class Meta:
        ordering = ['created_at']


class UserFeedback(models.Model):
    """Model for storing structured user feedback."""
    FEEDBACK_TYPE_CHOICES = [
        ('thumbs_up', 'Thumbs Up'),
        ('thumbs_down', 'Thumbs Down'),
        ('rating', 'Rating'),
        ('comment', 'Comment'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='feedback')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    rating = models.IntegerField(null=True, blank=True, help_text="Rating from 1-5")
    comment = models.TextField(blank=True, help_text="User's feedback comment")
    created_at = models.DateTimeField(default=timezone.now)
    
    # Additional metadata
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.feedback_type} feedback for {self.conversation.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "User feedback"
