from django.urls import path
from . import views

urlpatterns = [
    path('llm-status/', views.llm_status, name='llm-status'),
    path('conversations/', views.conversation_list, name='conversation-list'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation-detail'),
    path('conversations/<int:conversation_id>/delete/', views.conversation_delete, name='conversation-delete'),
    path('conversations/<int:conversation_id>/feedback/', views.submit_feedback, name='submit-feedback'),
    path('conversations/<int:conversation_id>/feedback/list/', views.conversation_feedback, name='conversation-feedback'),
]
