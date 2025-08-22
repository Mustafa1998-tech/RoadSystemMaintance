from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Issue, IssueComment, IssueAttachment, IssueHistory

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_by', 'assigned_to', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        (_('Assignment'), {
            'fields': ('created_by', 'assigned_to', 'due_date')
        }),
        (_('Location'), {
            'fields': ('location', 'latitude', 'longitude')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class IssueCommentInline(admin.StackedInline):
    model = IssueComment
    extra = 0
    readonly_fields = ('author', 'created_at', 'updated_at')
    fields = ('author', 'content', 'created_at', 'updated_at')
    
    def has_add_permission(self, request, obj=None):
        return False

class IssueAttachmentInline(admin.TabularInline):
    model = IssueAttachment
    extra = 0
    readonly_fields = ('file_preview', 'uploaded_by', 'uploaded_at', 'file_size')
    fields = ('file', 'file_preview', 'uploaded_by', 'uploaded_at', 'file_size')
    
    def file_preview(self, obj):
        if obj.file_type and obj.file_type.startswith('image/'):
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.file.url)
        return "-"
    file_preview.short_description = _('Preview')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

class IssueHistoryInline(admin.TabularInline):
    model = IssueHistory
    extra = 0
    readonly_fields = ('changed_by', 'changed_at', 'field', 'old_value', 'new_value')
    fields = ('changed_at', 'changed_by', 'field', 'old_value', 'new_value')
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(IssueComment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'issue', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'issue__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def truncated_content(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')
    truncated_content.short_description = _('Content')

@admin.register(IssueAttachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'issue', 'uploaded_by', 'uploaded_at', 'file_size_display')
    list_filter = ('uploaded_at', 'file_type')
    search_fields = ('file_name', 'issue__title')
    readonly_fields = ('uploaded_at', 'file_size', 'file_type')
    
    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = _('File Size')

@admin.register(IssueHistory)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('issue', 'field', 'changed_by', 'changed_at', 'truncated_old_value', 'truncated_new_value')
    list_filter = ('field', 'changed_at', 'changed_by')
    search_fields = ('issue__title', 'old_value', 'new_value')
    readonly_fields = ('issue', 'changed_by', 'changed_at', 'field', 'old_value', 'new_value')
    
    def truncated_old_value(self, obj):
        return (obj.old_value or '')[:50] + ('...' if obj.old_value and len(obj.old_value) > 50 else '')
    truncated_old_value.short_description = _('Old Value')
    
    def truncated_new_value(self, obj):
        return (obj.new_value or '')[:50] + ('...' if obj.new_value and len(obj.new_value) > 50 else '')
    truncated_new_value.short_description = _('New Value')
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
