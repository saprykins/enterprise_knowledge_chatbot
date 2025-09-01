from rest_framework import serializers
from .models import Conversation, Message, UserFeedback, DataSource, DocumentChunk, RAGQuery


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at']


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ['id', 'feedback_type', 'rating', 'comment', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    feedback_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages', 'message_count', 'feedback_count', 'use_company_data']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_feedback_count(self, obj):
        return obj.feedback.count()


class ConversationListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    feedback_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'last_message', 'feedback_count', 'use_company_data']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_feedback_count(self, obj):
        return obj.feedback.count()

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'role': last_message.role,
                'created_at': last_message.created_at
            }
        return None


class DocumentChunkSerializer(serializers.ModelSerializer):
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)

    class Meta:
        model = DocumentChunk
        fields = ['id', 'content', 'chunk_index', 'page_number', 'data_source_name', 'token_count', 'created_at']


class DataSourceSerializer(serializers.ModelSerializer):
    chunks = DocumentChunkSerializer(many=True, read_only=True)
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'source_type', 'file_path', 'url', 'is_active', 
            'status', 'created_at', 'updated_at', 'processing_started_at', 
            'processing_completed_at', 'error_message', 'total_chunks', 
            'total_tokens', 'chunks', 'chunk_count'
        ]
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at', 'processing_started_at',
            'processing_completed_at', 'error_message', 'total_chunks', 'total_tokens'
        ]

    def get_chunk_count(self, obj):
        return obj.chunks.count()


class DataSourceListSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'source_type', 'is_active', 'status', 
            'created_at', 'total_chunks', 'total_tokens', 'chunk_count'
        ]

    def get_chunk_count(self, obj):
        return obj.chunks.count()


class RAGQuerySerializer(serializers.ModelSerializer):
    retrieved_chunks = DocumentChunkSerializer(many=True, read_only=True)

    class Meta:
        model = RAGQuery
        fields = [
            'id', 'query', 'response', 'retrieved_chunks', 'created_at',
            'retrieval_time', 'generation_time', 'total_tokens_used'
        ]
        read_only_fields = [
            'id', 'response', 'retrieved_chunks', 'created_at',
            'retrieval_time', 'generation_time', 'total_tokens_used'
        ]
