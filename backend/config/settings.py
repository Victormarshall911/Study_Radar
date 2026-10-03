"""
Django settings for Study Radar backend.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from root or backend directory
env_path = BASE_DIR.parent / '.env'
if not env_path.exists():
    env_path = BASE_DIR / '.env'
load_dotenv(env_path)

# Add apps directory to sys.path
sys.path.insert(0, str(BASE_DIR))

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'study-radar-dev-secret-key-default-not-for-prod')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,backend,0.0.0.0').split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Study Radar apps
    'apps.geography.apps.GeographyConfig',
    'apps.sources.apps.SourcesConfig',
    'apps.opportunities.apps.OpportunitiesConfig',
    'apps.crawling.apps.CrawlingConfig',
    'apps.classification.apps.ClassificationConfig',
    'apps.notifications.apps.NotificationsConfig',
    'apps.users.apps.UsersConfig',
    'apps.analytics.apps.AnalyticsConfig',
    'apps.tasks.apps.TasksConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Support PostgreSQL and graceful fallback to SQLite for local tests/standalone execution
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
DB_NAME = os.getenv('DB_NAME', 'studyradar')
DB_USER = os.getenv('DB_USER', 'studyradar')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'studyradar_password')
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')

if os.getenv('USE_SQLITE', 'False').lower() in ('true', '1') or 'test' in sys.argv or 'pytest' in sys.modules:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    if origin.strip()
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {
    'discover-active-sources-hourly': {
        'task': 'apps.tasks.tasks.schedule_all_active_sources',
        'schedule': 3600.0,
    },
    'cleanup-expired-opportunities-daily': {
        'task': 'apps.tasks.tasks.cleanup_expired_opportunities',
        'schedule': 86400.0,
    },
}

# ==============================================================================
# STUDY RADAR CORE PRODUCT CONFIGURATION
# ==============================================================================
FRESHNESS_WINDOW_DAYS = int(os.getenv('FRESHNESS_WINDOW_DAYS', '7'))
CONFIDENCE_THRESHOLD_DATE = float(os.getenv('CONFIDENCE_THRESHOLD_DATE', '0.70'))
CONFIDENCE_THRESHOLD_GEO = float(os.getenv('CONFIDENCE_THRESHOLD_GEO', '0.70'))
CONFIDENCE_THRESHOLD_CLASSIFICATION = float(os.getenv('CONFIDENCE_THRESHOLD_CLASSIFICATION', '0.70'))

# AI Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'mock')
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')
AI_API_BASE = os.getenv('AI_API_BASE', 'https://api.openai.com/v1')

# Notifications Configuration
TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'False').lower() in ('true', '1')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

EMAIL_NOTIFICATION_ENABLED = os.getenv('EMAIL_NOTIFICATION_ENABLED', 'False').lower() in ('true', '1')
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('SMTP_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_HOST_USER = os.getenv('SMTP_USERNAME', '')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() in ('true', '1')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_FROM', 'alerts@studyradar.local')
ALERT_RECIPIENT_EMAIL = os.getenv('ALERT_RECIPIENT_EMAIL', 'user@example.com')

NOTIFICATION_LOCAL_LOG_ENABLED = os.getenv('NOTIFICATION_LOCAL_LOG_ENABLED', 'True').lower() in ('true', '1')
NOTIFICATION_LOG_PATH = BASE_DIR / 'logs' / 'notifications.log'

# Crawler & Security
CRAWLER_USER_AGENT = os.getenv('CRAWLER_USER_AGENT', 'StudyRadarBot/1.0 (+https://studyradar.local/bot; contact@studyradar.local)')
CRAWLER_DEFAULT_TIMEOUT = int(os.getenv('CRAWLER_DEFAULT_TIMEOUT', '15'))
CRAWLER_MAX_RETRIES = int(os.getenv('CRAWLER_MAX_RETRIES', '3'))
SSRF_PROTECTION_ENABLED = os.getenv('SSRF_PROTECTION_ENABLED', 'True').lower() in ('true', '1')

# User Settings
DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'Africa/Lagos')
