# TonyTheCoderPortfolio/settings.py
import os
from pathlib import Path
import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
env_path = BASE_DIR / '.env'
dotenv.load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-insecure-key-for-dev-portfolio') # Changed fallback for clarity
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

    # Third-party apps (review if needed for portfolio)
    'ckeditor',
    'ckeditor_uploader',
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

ROOT_URLCONF = 'TonyTheCoderPortfolio.urls' # Updated project name

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Project-level templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'portfolio_app.context_processors.global_settings', # If you create this for sitewide variables
            ],
        },
    },
]

WSGI_APPLICATION = 'TonyTheCoderPortfolio.wsgi.application' # Updated project name

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC' # Consider changing to your local timezone, e.g., 'America/New_York'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'

# Directories where Django will look for static files in addition to each app's 'static' directory.
# This is where your project-level static files (like global CSS, JS, images not tied to Vite) go.
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# The absolute path to the directory where collectstatic will collect static files for deployment.
# THIS MUST BE DEFINED.
STATIC_ROOT = BASE_DIR / 'staticfiles_production'

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Django Vite Settings ---
# Where Vite will build its assets for Django to serve in production
DJANGO_VITE_ASSETS_PATH = BASE_DIR / "static" / "dist"
# Use Vite's dev server in DEBUG mode for HMR, and manifest in production
DJANGO_VITE_DEV_MODE = DEBUG

# --- Authentication Settings ---
LOGIN_URL = '/accounts/login/'
# For your portfolio, you might redirect to the portfolio page or homepage after login
LOGIN_REDIRECT_URL = '/' # Or '/portfolio/' or '/admin-dashboard/' (your new staff dashboard)
LOGOUT_REDIRECT_URL = '/'

# --- CKEditor Settings (Optional: remove if not using CKEditor for portfolio/blog) ---
CKEDITOR_UPLOAD_PATH = "uploads/ckeditor/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
    'small': { # Example of a smaller toolbar for short descriptions if needed
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['Link', 'Unlink'],
            ['NumberedList', 'BulletedList'],
            ['Undo', 'Redo'],
            ['Source']
        ],
        'height': 150,
        'width': '100%',
    }
}

# --- QuickBooks Online API Settings (Optional: remove if not using for portfolio) ---
QBO_CLIENT_ID = os.environ.get('QBO_CLIENT_ID')
QBO_CLIENT_SECRET = os.environ.get('QBO_CLIENT_SECRET')
QBO_SANDBOX_REDIRECT_URI = os.environ.get('QBO_SANDBOX_REDIRECT_URI')
QBO_ENVIRONMENT = os.environ.get('QBO_ENVIRONMENT', 'sandbox')