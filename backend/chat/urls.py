from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # LLM Status
    path('llm-status/', views.llm_status, name='llm-status'),
    
    # Conversations
    path('conversations/', views.conversation_list, name='conversation-list'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation-detail'),
    path('conversations/<int:conversation_id>/delete/', views.conversation_delete, name='conversation-delete'),
    path('conversations/<int:conversation_id>/feedback/', views.submit_feedback, name='submit-feedback'),
    path('conversations/<int:conversation_id>/feedback/list/', views.conversation_feedback, name='conversation-feedback'),
    
    # RAG Admin
    path('data-sources/', views.data_sources, name='data-sources'),
    path('data-sources/<uuid:data_source_id>/', views.data_source_detail, name='data-source-detail'),
    path('rag-stats/', views.rag_stats, name='rag-stats'),
    path('conversations/<int:conversation_id>/rag-queries/', views.rag_queries, name='rag-queries'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
