from rest_framework import serializers
from .models import Conversation, Message, UserFeedback


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
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages', 'message_count', 'feedback_count']

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
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'last_message', 'feedback_count']

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
