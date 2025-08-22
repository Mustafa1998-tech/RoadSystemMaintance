from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class Issue(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')
    
    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        CRITICAL = 'critical', _('Critical')
    
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    priority = models.CharField(
        _('priority'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_issues',
        verbose_name=_('created by')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
        verbose_name=_('assigned to')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    due_date = models.DateTimeField(_('due date'), null=True, blank=True)
    location = models.CharField(_('location'), max_length=255, blank=True)
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('issue')
        verbose_name_plural = _('issues')
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class IssueComment(models.Model):
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('issue')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='issue_comments',
        verbose_name=_('author')
    )
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
    
    def __str__(self):
        return f"Comment by {self.author} on {self.issue}"

class IssueAttachment(models.Model):
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('issue')
    )
    file = models.FileField(
        _('file'),
        upload_to='issues/attachments/%Y/%m/%d/'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issue_attachments',
        verbose_name=_('uploaded by')
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    file_name = models.CharField(_('file name'), max_length=255)
    file_size = models.PositiveIntegerField(_('file size'))
    file_type = models.CharField(_('file type'), max_length=100)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')
    
    def __str__(self):
        return self.file_name
    
    def save(self, *args, **kwargs):
        if not self.file_name and hasattr(self.file, 'name'):
            self.file_name = self.file.name
        if not self.file_type and hasattr(self.file, 'content_type'):
            self.file_type = self.file.content_type
        if not self.file_size and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)

class IssueHistory(models.Model):
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('issue')
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issue_changes',
        verbose_name=_('changed by')
    )
    changed_at = models.DateTimeField(_('changed at'), auto_now_add=True)
    field = models.CharField(_('field'), max_length=50)
    old_value = models.TextField(_('old value'), blank=True, null=True)
    new_value = models.TextField(_('new value'), blank=True, null=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = _('history')
        verbose_name_plural = _('history')
    
    def __str__(self):
        return f"{self.field} changed by {self.changed_by} at {self.changed_at}"
