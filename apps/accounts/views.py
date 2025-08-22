from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.utils import timezone
from django_rest_passwordreset.views import ResetPasswordConfirm, ResetPasswordRequestToken

from .serializers import (
    UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer,
    ChangePasswordSerializer, UpdateProfileSerializer
)
from .models import UserActivity

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user with the given details.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserLoginView(TokenObtainPairView):
    """
    Authenticate a user and return JWT tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateProfileSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(UserSerializer(instance=self.get_object()).data)

class ChangePasswordView(APIView):
    """
    Change the current user's password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            return Response(
                {"message": "Password updated successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserActivityView(generics.ListAPIView):
    """
    Get the activity log for the current user.
    """
    serializer_class = None  # We'll use a custom response
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by('-timestamp')
    
    def list(self, request, *args, **kwargs):
        activities = self.get_queryset()
        data = [{
            'action': activity.action,
            'timestamp': activity.timestamp,
            'ip_address': activity.ip_address,
            'user_agent': activity.user_agent
        } for activity in activities]
        return Response(data)

class CustomPasswordResetConfirm(ResetPasswordConfirm):
    """
    Custom password reset confirmation view.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            # Log password reset activity
            user = User.objects.get(email=request.data.get('email'))
            UserActivity.objects.create(
                user=user,
                action='Password reset successful',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class CustomPasswordResetRequest(ResetPasswordRequestToken):
    """
    Custom password reset request view.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            # Log password reset request
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                UserActivity.objects.create(
                    user=user,
                    action='Password reset requested',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except User.DoesNotExist:
                pass  # Don't reveal if user exists or not
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
