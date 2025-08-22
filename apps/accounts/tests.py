from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
import json

User = get_user_model()

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.password_reset_url = reverse('password_reset:reset-password-request')
        self.password_reset_confirm_url = reverse('password_reset:reset-password-confirm')
        self.password_reset_validate_url = reverse('password_reset:reset-password-validate')

    def test_password_reset_request_success(self):
        """Test successful password reset request"""
        data = {'email': 'test@example.com'}
        response = self.client.post(
            self.password_reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'OK')

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(
            self.password_reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_success(self):
        """Test successful password reset confirmation"""
        # First request a password reset to get a token
        self.client.post(
            self.password_reset_url,
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        
        # Get the token from the database
        from django_rest_passwordreset.models import ResetPasswordToken
        token = ResetPasswordToken.objects.get(user=self.user)
        
        # Test password reset confirmation
        data = {
            'token': token.key,
            'password': 'newtestpass123'
        }
        response = self.client.post(
            self.password_reset_confirm_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'OK')

    def test_password_reset_validate_token(self):
        """Test token validation"""
        # First request a password reset to get a token
        self.client.post(
            self.password_reset_url,
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        
        # Get the token from the database
        from django_rest_passwordreset.models import ResetPasswordToken
        token = ResetPasswordToken.objects.get(user=self.user)
        
        # Test token validation
        data = {'token': token.key}
        response = self.client.post(
            self.password_reset_validate_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'OK')

    def test_password_reset_invalid_token(self):
        """Test password reset with invalid token"""
        data = {
            'token': 'invalid-token-123',
            'password': 'newtestpass123'
        }
        response = self.client.post(
            self.password_reset_confirm_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
