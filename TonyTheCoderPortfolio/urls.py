# TonyTheCoderPortfolio/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    # path('qbo/', include('qbo_integration.urls')), # If keeping QBO
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # For CKEditor 5
    path("", include("portfolio_app.urls", namespace="portfolio_app")),  # Main app
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )  # If using django-vite in dev, this might not be strictly needed for Vite assets but good for other static files
