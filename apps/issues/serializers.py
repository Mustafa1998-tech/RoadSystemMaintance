from rest_framework import serializers
from .models import Issue, IssueComment, IssueAttachment

class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for the Issue model
    """
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username', allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'location', 'created_at',
            'updated_at', 'created_by', 'created_by_username',
            'assigned_to', 'assigned_to_username'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

class IssueCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the IssueComment model
    """
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = IssueComment
        fields = ['id', 'issue', 'content', 'created_at', 'author', 'author_username']
        read_only_fields = ['created_at', 'author', 'issue']

class IssueAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the IssueAttachment model
    """
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')
    
    class Meta:
        model = IssueAttachment
        fields = ['id', 'issue', 'file', 'uploaded_at', 'uploaded_by', 'uploaded_by_username']
        read_only_fields = ['uploaded_at', 'uploaded_by', 'issue']
