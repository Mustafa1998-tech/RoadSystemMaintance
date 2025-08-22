from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Issues
    path('issues/', views.issue_list, name='issue-list'),  # Changed from 'list' to 'issue-list'
    path('issues/create/', views.issue_create, name='create'),
    path('issues/<int:pk>/', views.issue_detail, name='detail'),
    path('issues/<int:pk>/update/', views.issue_update, name='update'),
    path('issues/<int:pk>/delete/', views.issue_delete, name='delete'),
    path('issues/map/', views.issue_map, name='map'),  
    path('issues/<int:pk>/update-status/', views.update_issue_status_view, name='update-status'),
    
    # Comments
    path('issues/<int:pk>/comments/add/', views.add_comment, name='add-comment'),
    
    # Attachments
    path('issues/<int:pk>/attachments/upload/', views.upload_attachment, name='upload-attachment'),
    path('attachments/<int:pk>/delete/', views.delete_attachment, name='delete-attachment'),
]
