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
