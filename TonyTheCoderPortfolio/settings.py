# TonyTheCoderPortfolio/settings.py
import os
from pathlib import Path
import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
env_path = BASE_DIR / '.env'
dotenv.load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-insecure-key-for-dev-portfolio')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [] # Add your domain names here for production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party apps
    'django_ckeditor_5',

    # Vite integration
    'django_vite',

    # Your apps
    'portfolio_app',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TonyTheCoderPortfolio.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles_production'

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Django Vite Settings ---
DJANGO_VITE_ASSETS_PATH = BASE_DIR / "static" / "dist"
DJANGO_VITE_DEV_MODE = DEBUG

# Explicitly set the Vite Dev Server URL.
# This should be the root of your Vite dev server, without any subpaths.
DJANGO_VITE_DEV_SERVER_URL = 'http://localhost:5173'

# Comment out the individual components if using the full URL above.
# DJANGO_VITE_DEV_SERVER_PROTOCOL = 'http'
# DJANGO_VITE_DEV_SERVER_HOST = 'localhost'
# DJANGO_VITE_DEV_SERVER_PORT = 5173

# This prefix is applied to asset paths *after* the Vite server URL and Vite's `base`.
# It should be empty if Vite's `base` already includes the necessary prefix (like '/static/').
DJANGO_VITE_STATIC_URL_PREFIX = ''

# --- Authentication Settings ---
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# --- CKEditor 5 Settings ---
# (Your CKEditor settings would go here if you had them)
