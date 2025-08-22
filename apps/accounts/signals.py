from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.signals import user_logged_in as auth_user_logged_in
from django.contrib.auth.signals import user_logged_out as auth_user_logged_out

from .models import UserActivity

User = get_user_model()

def log_user_activity(user, action, request=None):
    """Helper function to log user activity"""
    ip_address = None
    user_agent = None
    
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Truncate if too long
    
    # Use transaction.on_commit to ensure the activity is only logged if the transaction succeeds
    transaction.on_commit(
        lambda: UserActivity.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent
        )
    )

@receiver(post_save, sender=User)
def user_created_or_updated(sender, instance, created, **kwargs):
    """Log when a user is created or updated"""
    if created:
        action = 'User account created'
    else:
        action = 'User account updated'
    
    # Get the request if available
    from django.core.handlers.wsgi import WSGIRequest
    request = None
    for entry in reversed(WSGIRequest.__mro__):
        if hasattr(entry, 'META') and hasattr(entry, 'user'):
            request = entry
            break
    
    log_user_activity(instance, action, request)

@receiver(auth_user_logged_in)
def user_logged_in(sender, request, user, **kwargs):
    """Log when a user logs in"""
    log_user_activity(user, 'User logged in', request)

@receiver(auth_user_logged_out)
def user_logged_out(sender, request, user, **kwargs):
    """Log when a user logs out"""
    if user and user.is_authenticated:
        log_user_activity(user, 'User logged out', request)

@receiver(pre_save, sender=User)
def user_password_changed(sender, instance, **kwargs):
    """Log when a user changes their password"""
    if not instance.pk:
        return  # New user, not a password change
    
    try:
        old_password = User.objects.get(pk=instance.pk).password
        if old_password != instance.password:
            log_user_activity(instance, 'Password changed')
    except User.DoesNotExist:
        pass  # User doesn't exist yet
