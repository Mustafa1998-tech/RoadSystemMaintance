from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView
from .views import WelcomeView

urlpatterns = [
    # Home page
    path('', WelcomeView.as_view(), name='welcome'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    
    # Admin site
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Endpoints
    path('api/auth/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('api/password_reset/', include('django_rest_passwordreset.urls')),
    
    # Issues URLs - both API and frontend
    path('issues/', include('apps.issues.urls', namespace='issues')),  # Frontend URLs
    path('api/issues/', include('apps.issues.api_urls', namespace='api-issues')),  # API URLs
]

# Serve media files in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler400 = 'road_maintenance.views.bad_request'
handler403 = 'road_maintenance.views.permission_denied'
handler404 = 'road_maintenance.views.page_not_found'
handler500 = 'road_maintenance.views.server_error'
