# qbo_integration/urls.py
from django.urls import path
from . import views

app_name = 'qbo_integration'

urlpatterns = [
    path('connect/', views.qbo_connect, name='connect'),
    path('callback/', views.qbo_callback, name='callback'),
    # We'll add an 'auth_success' and maybe 'disconnect' later
]