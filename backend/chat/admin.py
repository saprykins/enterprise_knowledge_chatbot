from django.contrib import admin
from .models import Conversation, Message, UserFeedback, DataSource, DocumentChunk, RAGQuery


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'use_company_data', 'created_at', 'updated_at', 'message_count', 'feedback_count']
    list_filter = ['use_company_data', 'created_at', 'updated_at']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def feedback_count(self, obj):
        return obj.feedback.count()
    feedback_count.short_description = 'Feedback'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at', 'conversation']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'feedback_type', 'rating', 'created_at', 'ip_address']
    list_filter = ['feedback_type', 'rating', 'created_at', 'conversation']
    search_fields = ['comment', 'conversation__title']
    readonly_fields = ['created_at', 'user_agent', 'ip_address']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'message')


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'is_active', 'status', 'total_chunks', 'total_tokens', 'created_at']
    list_filter = ['source_type', 'is_active', 'status', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processing_started_at', 'processing_completed_at', 'total_chunks', 'total_tokens']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'source_type', 'file_path', 'url', 'is_active')
        }),
        ('Processing Status', {
            'fields': ('status', 'processing_started_at', 'processing_completed_at', 'error_message')
        }),
        ('Statistics', {
            'fields': ('total_chunks', 'total_tokens')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at')
        })
    )


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['id', 'data_source', 'chunk_index', 'page_number', 'token_count', 'created_at']
    list_filter = ['data_source', 'created_at']
    search_fields = ['content', 'data_source__name']
    readonly_fields = ['id', 'embedding_id', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('data_source')


@admin.register(RAGQuery)
class RAGQueryAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'query_preview', 'retrieval_time', 'generation_time', 'total_tokens_used', 'created_at']
    list_filter = ['created_at', 'conversation']
    search_fields = ['query', 'response', 'conversation__title']
    readonly_fields = ['id', 'created_at', 'retrieval_time', 'generation_time', 'total_tokens_used']
    
    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation')
