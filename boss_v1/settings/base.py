
from pathlib import Path
import os
import environ
import logging
import sys
from boss_admin.log_utils import StreamToLogger, ExcludeWarningsFilter

env = environ.Env()
environ.Env.read_env()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))).replace('\\','/')
# BASE_DIR = os.path.join(os.path.dirname(__file__)).replace('\\','/')
# print("the exact base dir", BASE_DIR)

# with open(os.path.join(BASE_DIR, 'django_secret_key.txt')) as f:
#     SECRET_KEY = f.read().strip()
SECRET_KEY = 'rl)=kdz1u7z4+m*35khwee88!!!@azle3z+l)bc@_h6@r9k2yp'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
# print(STATIC_ROOT, STATIC_URL)

SESSION_EXPIRE_SECONDS = 900  # 15 min
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = '/logout'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
USE_X_FORWARDED_HOST = True

LOG_FILE = os.path.join(BASE_DIR, "/escalation_files/escaltion.log")
# REGISTERS_LOG = os.path.join(BASE_DIR, "/registers_log/registers.log")

INSTALLED_APPS = [
    'smuggler',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'notifications_app',
    'boss_admin',
    'preliminaryscreeningcommittee_review'    
]

MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "tenants.middlewares.TenantMiddleware",
]

ROOT_URLCONF = 'boss_v1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications_app.context_processors.notifications'
            ],
        },
    },
]

WSGI_APPLICATION = 'boss_v1.wsgi.application'

DATABASE_ROUTERS = ["tenants.router.TenantRouter"]

# Escalation File logs
REGISTERS_LOG = os.path.join(BASE_DIR, 'registers_log/registers.log')
SCREENING_COMMITTEE_LOG = os.path.join(BASE_DIR, 'Logs/psc.log')
date_strftime_format = "%d-%b-%Y %H:%M:%S %p"
msg_format = '%(asctime)s :: %(levelname)s :: %(message)s'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AD_LOGIN = True

# if env('BOSS_ENV') == "prod":
#     print('prod', env('BOSS_ENV'))
#     AD_LOGIN = False
# else:
#     print('local')
#     AD_LOGIN = False
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Calcutta'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
KEYS_ROOT = os.path.join(BASE_DIR, 'boss_admin/ED_Key')
print('KEYS_ROOT',KEYS_ROOT)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'
DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520 #20mb

"""
System Logs
"""

# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_LOG_DIR = os.path.join(BASE_DIR, 'CustomLog')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },

    'filters': {
        'exclude_warnings': {
            '()': 'boss_admin.log_utils.ExcludeWarningsFilter',
        },
    },

    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'boss_admin.log_utils.DailySizeRotatingFileHandler',
            'formatter': 'verbose',
            'filters': ['exclude_warnings'],
            'base_dir': BASE_LOG_DIR,
            'filename_prefix': 'django',
            'maxBytes': 5 * 1024 * 1024,  # 5MB
            'encoding': 'utf-8',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'stdout_logger': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Redirect print() to both terminal and logger
stdout_logger = logging.getLogger('stdout_logger')
sys.stdout = StreamToLogger(stdout_logger, logging.INFO, stream=sys.__stdout__)
sys.stderr = StreamToLogger(stdout_logger, logging.ERROR, stream=sys.__stderr__)


