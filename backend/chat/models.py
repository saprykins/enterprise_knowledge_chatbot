from django.db import models
from django.utils import timezone
import uuid


class Conversation(models.Model):
    """Model for storing chat conversations."""
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    USE_COMPANY_DATA_CHOICES = [
        ('use', 'Use'),
        ('both', 'Both'),
        ('not_use', 'Not Use'),
    ]
    use_company_data = models.CharField(
        max_length=10, 
        choices=USE_COMPANY_DATA_CHOICES, 
        default='not_use'
    )

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


class DataSource(models.Model):
    """Model for storing data source information."""
    SOURCE_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('confluence', 'Confluence'),
        ('jira', 'Jira'),
        ('sharepoint', 'SharePoint'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    file_path = models.FileField(upload_to='documents/', null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metadata
    total_chunks = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.source_type})"

    class Meta:
        ordering = ['-created_at']


class DocumentChunk(models.Model):
    """Model for storing document chunks and their embeddings."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    chunk_index = models.IntegerField()
    page_number = models.IntegerField(null=True, blank=True)
    embedding_id = models.CharField(max_length=255, unique=True)  # ChromaDB ID
    created_at = models.DateTimeField(default=timezone.now)
    
    # Metadata
    token_count = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Chunk {self.chunk_index} from {self.data_source.name}"

    class Meta:
        ordering = ['data_source', 'chunk_index']
        unique_together = ['data_source', 'chunk_index']


class RAGQuery(models.Model):
    """Model for storing RAG query history."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='rag_queries')
    query = models.TextField()
    retrieved_chunks = models.ManyToManyField(DocumentChunk, related_name='queries')
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    # Performance metrics
    retrieval_time = models.FloatField(null=True, blank=True)  # seconds
    generation_time = models.FloatField(null=True, blank=True)  # seconds
    total_tokens_used = models.IntegerField(default=0)

    def __str__(self):
        return f"RAG Query: {self.query[:50]}..."

    class Meta:
        ordering = ['-created_at']
