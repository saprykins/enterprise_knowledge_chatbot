from django.contrib import admin
from .models import Conversation, Message, UserFeedback


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'feedback_count']
    list_filter = ['created_at', 'updated_at']
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
