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
    'django_ckeditor_5', # Correct for CKEditor 5

    # 'qbo_integration', # Optional: remove if not using QBO for the portfolio

    # Vite integration
    'django_vite',

    # Your apps
    'portfolio_app', # Your renamed main app
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
                # 'portfolio_app.context_processors.global_settings', # REMOVED for now
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
STATIC_ROOT = BASE_DIR / 'staticfiles_production' # Essential for collectstatic

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Django Vite Settings ---
DJANGO_VITE_ASSETS_PATH = BASE_DIR / "static" / "dist"
DJANGO_VITE_DEV_MODE = DEBUG

# --- Authentication Settings ---
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# --- CKEditor 5 Settings ---
# These are examples; refer to django-ckeditor-5 documentation for full options
# Remove the old CKEDITOR_UPLOAD_PATH and CKEDITOR_CONFIGS for version 4
# DJANGO_CKEDITOR_5_UPLOAD_PATH = "uploads/ckeditor5/" # For default image uploads with django-ckeditor-5
# DJANGO_CKEDITOR_5_CONFIGS = {
# 'default': {
# 'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'imageUpload'],
#         # You might need to configure an image upload adapter for 'imageUpload' to work properly
#         # 'image': {
#         #     'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight'],
#         #     'styles': [
#         #         'alignLeft', 'alignCenter', 'alignRight'
#         #     ]
#         # }
#     },
# 'small_toolbar': { # Example of a custom config
# 'toolbar': ['bold', 'italic', 'link', 'bulletedList'],
# 'height': 150,
#     },
# 'richtext': True, # Generally not needed here, feature enablement is usually in toolbar config
# }


