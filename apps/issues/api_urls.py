from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'api-issues'

urlpatterns = [
    # API endpoints for issues
    path('', views.IssueListCreateAPIView.as_view(), name='issue-list'),
    path('<int:pk>/', views.issue_detail, name='issue-detail'),
    path('<int:pk>/update/', views.issue_update, name='issue-update'),
    path('<int:pk>/delete/', views.issue_delete, name='issue-delete'),
    path('<int:issue_id>/comments/add/', views.add_comment, name='add-comment'),
    path('<int:issue_id>/attachments/upload/', views.upload_attachment, name='upload-attachment'),
    path('<int:pk>/status/', views.update_issue_status, name='update-status'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
