from django.db import models
from django.conf import settings

class MediaFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_files'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file.name} ({self.uploaded_by})"

    class Meta:
        ordering = ['-created_at']
