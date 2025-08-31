from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, UserFeedback
from .serializers import ConversationSerializer, ConversationListSerializer, MessageSerializer, UserFeedbackSerializer
from .services import LLMService


@api_view(['GET', 'POST'])
def conversation_list(request):
    """List all conversations or create a new one."""
    if request.method == 'GET':
        conversations = Conversation.objects.all()
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create new conversation
        conversation = Conversation.objects.create()
        
        # Add user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=request.data.get('message', '')
        )
        
        # Generate title for the conversation
        llm_service = LLMService()
        title = llm_service.generate_conversation_title(user_message.content)
        conversation.title = title
        conversation.save()
        
        # Generate assistant response
        messages_for_llm = [
            {'role': msg.role, 'content': msg.content}
            for msg in conversation.messages.all()
        ]
        
        assistant_response = llm_service.generate_response(messages_for_llm)
        
        # Save assistant response
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=assistant_response
        )
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def conversation_detail(request, conversation_id):
    """Get conversation details or add a new message."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.method == 'GET':
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Add user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=request.data.get('message', '')
        )
        
        # Generate assistant response
        llm_service = LLMService()
        messages_for_llm = [
            {'role': msg.role, 'content': msg.content}
            for msg in conversation.messages.all()
        ]
        
        assistant_response = llm_service.generate_response(messages_for_llm)
        
        # Save assistant response
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=assistant_response
        )
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


@api_view(['DELETE'])
def conversation_delete(request, conversation_id):
    """Delete a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def submit_feedback(request, conversation_id):
    """Submit user feedback for a conversation or specific message."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    feedback_data = {
        'conversation': conversation,
        'feedback_type': request.data.get('feedback_type'),
        'rating': request.data.get('rating'),
        'comment': request.data.get('comment', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'ip_address': request.META.get('REMOTE_ADDR')
    }
    
    # If feedback is for a specific message
    message_id = request.data.get('message_id')
    if message_id:
        try:
            message = Message.objects.get(id=message_id, conversation=conversation)
            feedback_data['message'] = message
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
    
    feedback = UserFeedback.objects.create(**feedback_data)
    serializer = UserFeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def conversation_feedback(request, conversation_id):
    """Get all feedback for a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    feedback = conversation.feedback.all()
    serializer = UserFeedbackSerializer(feedback, many=True)
    return Response(serializer.data)
