from django.http import JsonResponse
from rest_framework import status
from django.views.generic import TemplateView

class WelcomeView(TemplateView):
    template_name = 'welcome.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_docs_url'] = '/api/docs/'
        context['admin_url'] = '/admin/'
        return context

def bad_request(request, exception, *args, **kwargs):
    """Handle 400 Bad Request errors"""
    return JsonResponse(
        {"error": "Bad Request", "message": str(exception)},
        status=status.HTTP_400_BAD_REQUEST
    )

def permission_denied(request, exception, *args, **kwargs):
    """Handle 403 Forbidden errors"""
    return JsonResponse(
        {"error": "Permission Denied", "message": str(exception)},
        status=status.HTTP_403_FORBIDDEN
    )

def page_not_found(request, exception, *args, **kwargs):
    """Handle 404 Not Found errors"""
    return JsonResponse(
        {"error": "Not Found", "message": "The requested resource was not found"},
        status=status.HTTP_404_NOT_FOUND
    )

def server_error(request, *args, **kwargs):
    """Handle 500 Internal Server errors"""
    return JsonResponse(
        {"error": "Internal Server Error", "message": "An unexpected error occurred"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
