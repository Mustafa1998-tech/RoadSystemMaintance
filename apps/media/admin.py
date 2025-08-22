from django.contrib import admin
from .models import MediaFile

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('file', 'uploaded_by__username')
    date_hierarchy = 'created_at'
