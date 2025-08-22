from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, UserLoginView, UserProfileView,
    ChangePasswordView, UserActivityView, CustomPasswordResetConfirm,
    CustomPasswordResetRequest
)

app_name = 'accounts'  # Define the namespace for the app

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='welcome'), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password reset endpoints
    path('password/reset/', CustomPasswordResetRequest.as_view(), name='password_reset'),
    path('password/reset/confirm/', CustomPasswordResetConfirm.as_view(), name='password_reset_confirm'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='password_change'),
    path('activity/', UserActivityView.as_view(), name='user_activity'),
]
