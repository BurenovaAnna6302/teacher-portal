import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Загружаем переменные из .env (только для локальной разработки)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ (обязательно переопределить на сервере!)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')

# Режим отладки – на сервере всегда False
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Разрешённые хосты (из переменной окружения, без пробелов)
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')]

# Доверенные источники для CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://ja-v-tempe.ru',
    'https://явтемпе.рф',
    'https://burenovaanna6302-teacher-portal-a1f8.twc1.net',
]

# КЛЮЧЕВЫЕ НАСТРОЙКИ ДЛЯ ПРОКСИ (Timeweb Cloud)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Настройки CSRF и сессий
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Логирование CSRF-ошибок
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.security.csrf': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Коды для двухфакторной аутентификации
ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE', '')
ADMIN_BACKUP_CODE = os.getenv('ADMIN_BACKUP_CODE', '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'main',
    'about',
    'news',
    'events',
    'materials',
    'documents',
    'surveys',
    'members',
    'teachers',
    'account',
    'admin_panel',
    'success_practices',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
                'django.template.context_processors.static',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# База данных (из переменной окружения DATABASE_URL)
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 1209600

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ===== Статика =====
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'main/static',
    BASE_DIR / 'teachers/static',
    BASE_DIR / 'account/static',
    BASE_DIR / 'admin_panel/static',
    BASE_DIR / 'news/static',
    BASE_DIR / 'events/static',
    BASE_DIR / 'materials/static',
    BASE_DIR / 'documents/static',
    BASE_DIR / 'surveys/static',
    BASE_DIR / 'members/static',
    BASE_DIR / 'success_practices/static',
]

# ===== Медиа (S3 Timeweb Cloud) =====
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Данные для подключения к S3 (из переменных окружения)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'teacher-portal-media'
AWS_S3_REGION_NAME = 'ru-1'
AWS_S3_ENDPOINT_URL = 'https://s3.twcstorage.ru'

# Правильный домен для формирования публичных ссылок
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.twcstorage.ru'

# Публичный доступ для всех загружаемых объектов
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

# Параметры объектов (кэширование + ACL)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
    'ACL': 'public-read',
}

# Медиа URL будет указывать на S3
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# Локальная папка для медиа (не используется при S3, но оставляем)
MEDIA_ROOT = BASE_DIR / 'media'

# ===== Ограничения загрузки =====
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/account/profile/'
LOGOUT_REDIRECT_URL = '/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'