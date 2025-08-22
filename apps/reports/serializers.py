from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = Report
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
