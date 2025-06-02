# LehmanConstructionDjangoD/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Lehman Custom Construction Admin"
admin.site.site_title = "Lehman Admin Portal"
admin.site.index_title = "Welcome to the Lehman Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # <-- Standard auth URLs
    path('qbo/', include('qbo_integration.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
path('', include('portfolio_app.urls', namespace='portfolio_app')),
]

# Serve Media files in Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)