from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

from .models import Conversation, Message, UserFeedback, DataSource, DocumentChunk, RAGQuery
from .serializers import (
    ConversationSerializer, ConversationListSerializer, MessageSerializer, 
    UserFeedbackSerializer, DataSourceSerializer, DataSourceListSerializer,
    RAGQuerySerializer
)
from .services import LLMService
from .rag_service import RAGService
from .tasks import process_document_task, delete_document_chunks_task


@api_view(['GET'])
def llm_status(request):
    """Check LLM service status and model information."""
    llm_service = LLMService()
    model_info = llm_service.get_model_info()
    
    return Response({
        'status': 'ok' if 'API working' in model_info else 'error',
        'model_info': model_info,
        'github_configured': bool(llm_service.github_token)
    })


@api_view(['GET', 'POST'])
def conversation_list(request):
    """List all conversations or create a new one."""
    if request.method == 'GET':
        conversations = Conversation.objects.all()
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create new conversation
        use_company_data = request.data.get('use_company_data', False)
        conversation = Conversation.objects.create(use_company_data=use_company_data)
        
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
        if conversation.use_company_data:
            # Use RAG for company data
            rag_service = RAGService()
            assistant_response = rag_service.generate_rag_response(
                user_message.content, 
                conversation.id
            )
        else:
            # Use regular LLM
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
        if conversation.use_company_data:
            # Use RAG for company data
            rag_service = RAGService()
            assistant_response = rag_service.generate_rag_response(
                user_message.content, 
                conversation.id
            )
        else:
            # Use regular LLM
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


# RAG Admin Views
@api_view(['GET', 'POST'])
def data_sources(request):
    """List all data sources or create a new one."""
    if request.method == 'GET':
        data_sources = DataSource.objects.all()
        serializer = DataSourceListSerializer(data_sources, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Handle file upload
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        if not file.name.lower().endswith('.pdf'):
            return Response({'error': 'Only PDF files are supported'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save file
        file_path = f"documents/{uuid.uuid4()}_{file.name}"
        saved_path = default_storage.save(file_path, ContentFile(file.read()))
        
        # Create data source
        data_source = DataSource.objects.create(
            name=request.data.get('name', file.name),
            source_type='pdf',
            file_path=saved_path
        )
        
        # Trigger async processing
        process_document_task.delay(str(data_source.id))
        
        serializer = DataSourceSerializer(data_source)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def data_source_detail(request, data_source_id):
    """Get, update, or delete a data source."""
    data_source = get_object_or_404(DataSource, id=data_source_id)
    
    if request.method == 'GET':
        serializer = DataSourceSerializer(data_source)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Update data source (mainly for toggling active status)
        is_active = request.data.get('is_active')
        if is_active is not None:
            data_source.is_active = is_active
            data_source.save()
        
        serializer = DataSourceSerializer(data_source)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        # Delete data source and its chunks
        delete_document_chunks_task.delay(str(data_source.id))
        
        # Delete file
        if data_source.file_path:
            try:
                default_storage.delete(data_source.file_path.name)
            except:
                pass
        
        data_source.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def rag_stats(request):
    """Get RAG system statistics."""
    rag_service = RAGService()
    stats = rag_service.get_database_stats()
    return Response(stats)


@api_view(['GET'])
def rag_queries(request, conversation_id):
    """Get RAG queries for a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    queries = conversation.rag_queries.all()
    serializer = RAGQuerySerializer(queries, many=True)
    return Response(serializer.data)
