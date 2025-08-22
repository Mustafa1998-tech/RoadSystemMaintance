from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse

from .models import Issue, IssueComment, IssueAttachment, IssueHistory
from .forms import IssueForm, IssueCommentForm, IssueAttachmentForm
from rest_framework import generics, permissions
from .serializers import IssueSerializer

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard.html'
    context_object_name = 'recent_issues'
    paginate_by = 5
    
    def get_queryset(self):
        return Issue.objects.filter(
            Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issues = self.get_queryset()
        
        # Get counts for dashboard stats
        context['stats'] = {
            'open': issues.filter(status='open').count(),
            'in_progress': issues.filter(status='in_progress').count(),
            'resolved': issues.filter(status='resolved').count(),
            'assigned_to_me': issues.filter(assigned_to=self.request.user, status__in=['open', 'in_progress']).count(),
            'created_by_me': issues.filter(created_by=self.request.user).count()
        }
        
        # Get recent activity
        context['recent_activity'] = IssueHistory.objects.filter(
            Q(issue__created_by=self.request.user) | 
            Q(issue__assigned_to=self.request.user)
        ).select_related('issue', 'changed_by').order_by('-changed_at')[:10]
        
        context['user_full_name'] = self.request.user.get_full_name() if self.request.user.is_authenticated else 'Guest'
        
        return context

class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = 'issues/list.html'
    context_object_name = 'issues'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Issue.objects.all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        # Search
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
            
        # Filter by assigned to me
        if self.request.GET.get('assigned_to_me'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        # Filter by created by me
        if self.request.GET.get('created_by_me'):
            queryset = queryset.filter(created_by=self.request.user)
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = 'issues/detail.html'
    context_object_name = 'issue'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = IssueCommentForm()
        context['attachment_form'] = IssueAttachmentForm()
        context['comments'] = self.object.comments.select_related('author').all()
        context['attachments'] = self.object.attachments.all()
        context['history'] = self.object.history.select_related('changed_by').order_by('-changed_at')
        return context

class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'issues/form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Issue created successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('issues:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Issue'
        context['submit_text'] = 'Create Issue'
        return context

class IssueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'issues/form.html'
    
    def test_func(self):
        issue = self.get_object()
        return self.request.user == issue.created_by or self.request.user.is_staff
    
    def form_valid(self, form):
        # Create history for changed fields
        issue = self.get_object()
        for field in form.changed_data:
            if field not in ['updated_at', 'created_at']:  # Skip these fields
                IssueHistory.objects.create(
                    issue=issue,
                    changed_by=self.request.user,
                    field=field,
                    old_value=str(getattr(issue, field)),
                    new_value=str(form.cleaned_data[field])
                )
        
        response = super().form_valid(form)
        messages.success(self.request, 'Issue updated successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('issues:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Issue: {self.object.title}'
        context['submit_text'] = 'Update Issue'
        return context

class IssueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Issue
    template_name = 'issues/confirm_delete.html'
    success_url = reverse_lazy('issues:list')
    
    def test_func(self):
        issue = self.get_object()
        return self.request.user == issue.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Issue deleted successfully.')
        return super().delete(request, *args, **kwargs)

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = IssueComment
    form_class = IssueCommentForm
    
    def form_valid(self, form):
        form.instance.issue_id = self.kwargs['pk']
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        # Create history entry
        issue = self.object.issue
        IssueHistory.objects.create(
            issue=issue,
            changed_by=self.request.user,
            field='comment',
            new_value=f'Comment added: {form.cleaned_data["content"][:50]}...'
        )
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment': {
                    'content': self.object.content,
                    'author': self.object.author.get_full_name() or self.object.author.username,
                    'created_at': self.object.created_at.strftime('%b. %d, %Y, %I:%M %p'),
                    'avatar': self.object.author.profile_picture.url if hasattr(self.object.author, 'profile_picture') and self.object.author.profile_picture else ''
                }
            })
            
        messages.success(self.request, 'Comment added successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('issues:detail', kwargs={'pk': self.kwargs['pk']})

def upload_attachment(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if request.method == 'POST':
        form = IssueAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.issue = issue
            attachment.uploaded_by = request.user
            attachment.save()
            
            # Create history entry
            IssueHistory.objects.create(
                issue=issue,
                changed_by=request.user,
                field='attachment',
                new_value=f'File uploaded: {attachment.file_name}'
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'attachment': {
                        'file_name': attachment.file_name,
                        'file_url': attachment.file.url,
                        'file_type': attachment.file_type,
                        'file_size': attachment.file_size,
                        'uploaded_at': attachment.uploaded_at.strftime('%b. %d, %Y, %I:%M %p'),
                        'uploaded_by': attachment.uploaded_by.get_full_name() or attachment.uploaded_by.username
                    }
                })
                
            messages.success(request, 'File uploaded successfully.')
            return redirect('issues:detail', pk=issue.pk)
    
    return redirect('issues:detail', pk=issue.pk)

def update_issue_status(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        issue = get_object_or_404(Issue, pk=pk)
        status = request.POST.get('status')
        
        if status in dict(Issue.Status.choices):
            old_status = issue.status
            issue.status = status
            issue.save()
            
            # Create history entry
            IssueHistory.objects.create(
                issue=issue,
                changed_by=request.user,
                field='status',
                old_value=old_status,
                new_value=status
            )
            
            return JsonResponse({
                'success': True,
                'status': issue.get_status_display(),
                'status_class': status.replace('_', '-')
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def issue_list(request):
    issues = Issue.objects.all().order_by('-created_at')
    return render(request, 'issues/issue_list.html', {'issues': issues})

def issue_create(request):
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()
            messages.success(request, 'Issue created successfully.')
            return redirect('issue-detail', pk=issue.pk)
    else:
        form = IssueForm()
    return render(request, 'issues/form.html', {'form': form, 'title': 'Create Issue'})

def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    comments = issue.comments.all()
    attachments = issue.attachments.all()
    
    if request.method == 'POST':
        comment_form = IssueCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.issue = issue
            comment.created_by = request.user
            comment.save()
            return redirect('issues:issue-detail', pk=issue.pk)
    else:
        comment_form = IssueCommentForm()
    
    return render(request, 'issues/issue_detail.html', {
        'issue': issue,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': IssueAttachmentForm()
    })

def issue_update(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Issue updated successfully.')
            return redirect('issues:issue-detail', pk=issue.pk)
    else:
        form = IssueForm(instance=issue)
    return render(request, 'issues/issue_form.html', {'form': form, 'title': 'Update Issue'})

def issue_delete(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        issue.delete()
        messages.success(request, 'Issue deleted successfully.')
        return redirect('issues:issue-list')
    return render(request, 'issues/issue_confirm_delete.html', {'issue': issue})

def add_comment(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        form = IssueCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.created_by = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
    return redirect('issues:issue-detail', pk=issue.pk)

def upload_attachment_view(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        form = IssueAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.issue = issue
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, 'Attachment uploaded successfully.')
    return redirect('issues:issue-detail', pk=issue.pk)

def delete_attachment(request, pk):
    attachment = get_object_or_404(IssueAttachment, pk=pk)
    issue_pk = attachment.issue.pk
    attachment.delete()
    messages.success(request, 'Attachment deleted successfully.')
    return redirect('issues:issue-detail', pk=issue_pk)

def update_issue_status_view(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Issue.Status.choices):
            issue.status = new_status
            issue.save()
            messages.success(request, f'Issue status updated to {issue.get_status_display()}')
    return redirect('issues:issue-detail', pk=issue.pk)

def dashboard(request):
    # Get counts for different statuses
    status_counts = {}
    for status in dict(Issue.Status.choices).keys():
        status_counts[status] = Issue.objects.filter(status=status).count()
    
    # Get recent issues
    recent_issues = Issue.objects.all().order_by('-created_at')[:5]
    
    context = {
        'status_counts': status_counts,
        'recent_issues': recent_issues,
        'user_full_name': request.user.get_full_name() if request.user.is_authenticated else 'Guest',
    }
    return render(request, 'dashboard.html', context)

def issue_map(request):
    """
    View to display issues on an interactive map
    """
    # Get all issues with location data
    issues = Issue.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    context = {
        'issues': issues,
        'title': 'Issues Map',
    }
    return render(request, 'issues/issue_map.html', context)

class IssueListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating issues
    - Unauthenticated users can view and create issues (for development)
    - In production, you should enable authentication
    """
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests for development
    
    def perform_create(self, serializer):
        # Set the created_by field to the current user if authenticated, or None if not
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            # For development, you might want to set a default user or handle this differently
            # For now, we'll save without a user
            serializer.save()
