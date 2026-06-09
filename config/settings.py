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

# Разрешённые хосты – задаются через переменную окружения (на сервере – список доменов)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ✅ Добавлено: доверенные источники для CSRF-защиты (обязательно для HTTPS)
CSRF_TRUSTED_ORIGINS = [
    'https://burenkovaanna6302-teacher-portal-a1f8.twc1.net',
    'https://явтемпе.рф',           # ваш будущий домен
    'https://www.явтемпе.рф',       # если будете использовать www
]

# Коды для двухфакторной аутентификации администратора
ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE', '')
ADMIN_BACKUP_CODE = os.getenv('ADMIN_BACKUP_CODE', '')

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

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

# База данных – используем единую строку подключения DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# Сессии
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False      # При включенном HTTPS поставьте True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600

# Интернационализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы (CSS, JS, изображения)
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

# Медиафайлы
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ограничения на загрузку
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760   # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760   # 10 MB

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL для логина и редиректов
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/account/profile/'
LOGOUT_REDIRECT_URL = '/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'