from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationListSerializer, MessageSerializer
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
