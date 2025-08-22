from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Issue, IssueComment, IssueAttachment

User = get_user_model()

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            'title', 'description', 'status', 'priority', 
            'assigned_to', 'due_date', 'location', 
            'latitude', 'longitude'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Enter issue title')
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': _('Describe the issue in detail')
            }),
            'status': forms.Select(attrs={'class': 'input'}),
            'priority': forms.Select(attrs={'class': 'input'}),
            'assigned_to': forms.Select(attrs={'class': 'input'}),
            'due_date': forms.DateTimeInput(
                attrs={
                    'class': 'input',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'location': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Enter location or address')
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show active users in the assigned_to field
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        
        # Set initial assigned_to to current user if creating a new issue
        if not self.instance.pk and user:
            self.fields['assigned_to'].initial = user
        
        # Format the datetime for the datetime-local input
        if self.instance.due_date:
            self.initial['due_date'] = self.instance.due_date.strftime('%Y-%m-%dT%H:%M')

class IssueCommentForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': _('Add a comment...'),
                'x-data': '{ resize() { $el.style.height = \'auto\'; $el.style.height = $el.scrollHeight + \'px\' } }',
                'x-init': 'resize()',
                '@input': 'resize()',
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = ''

class IssueAttachmentForm(forms.ModelForm):
    class Meta:
        model = IssueAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'hidden',
                'x-ref': 'fileInput',
                '@change': 'fileName = $refs.fileInput.files[0] ? $refs.fileInput.files[0].name : \'No file chosen\''
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].label = ''
        self.fields['file'].required = True
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Limit file size to 10MB
            max_size = 10 * 1024 * 1024  # 10MB
            if file.size > max_size:
                raise forms.ValidationError(_('File size must be less than 10MB.'))
            
            # Validate file types
            valid_types = [
                'image/jpeg', 'image/png', 'image/gif',
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/plain'
            ]
            
            if file.content_type not in valid_types:
                raise forms.ValidationError(_('File type not supported.'))
        
        return file
