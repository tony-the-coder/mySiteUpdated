# LehmanConstructionDjangoD/settings.py
import os
from pathlib import Path
import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
dotenv.load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-insecure-key-for-dev')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'ckeditor',
    'ckeditor_uploader',
'django_vite',
'portfolio_app',
    'qbo_integration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TonyTheCoderPortfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TonyTheCoderPortfolio.wsgi.application'
DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3', } }
AUTH_PASSWORD_VALIDATORS = [ {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',}, ]
LANGUAGE_CODE = 'en-us'; TIME_ZONE = 'UTC'; USE_I18N = True; USE_TZ = True
STATIC_URL = 'static/'; STATICFILES_DIRS = [ BASE_DIR / 'static', ]
MEDIA_URL = '/media/'; MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Authentication Settings ---
LOGIN_URL = '/accounts/login/' # <-- USE STANDARD AUTH LOGIN URL
LOGIN_REDIRECT_URL = '/staff/dashboard/' # Default redirect after successful login (for staff now)
LOGOUT_REDIRECT_URL = '/' # <-- ADD THIS: Redirect to homepage after logout

# --- QuickBooks Online API Settings ---
QBO_CLIENT_ID = os.environ.get('QBO_CLIENT_ID')
QBO_CLIENT_SECRET = os.environ.get('QBO_CLIENT_SECRET')
QBO_SANDBOX_REDIRECT_URI = os.environ.get('QBO_SANDBOX_REDIRECT_URI')
QBO_ENVIRONMENT = os.environ.get('QBO_ENVIRONMENT', 'sandbox')

# --- CKEditor Settings ---
CKEDITOR_UPLOAD_PATH = "uploads/ckeditor/"
CKEDITOR_CONFIGS = { 'default': { 'toolbar': 'full', 'height': 300, 'width': '100%', }, }
# CSRF_COOKIE_HTTPONLY = False # Only if needed for CKEditor uploads