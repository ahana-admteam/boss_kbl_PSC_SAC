"""Minimal Django settings for pytest.

We avoid importing the project's real settings so the test suite is
independent from production/dev config — the production base.py wires
custom logging handlers and sys.stdout/stderr redirection that fight pytest.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "test-secret-key-not-for-prod"
DEBUG = True
ALLOWED_HOSTS = ["*"]
AD_LOGIN = False

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "notifications_app",
    "boss_admin",
    "preliminaryscreeningcommittee_review",
    "tenants",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "tenants.middlewares.TenantMiddleware",
]

ROOT_URLCONF = "tests.urls_test"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# Don't install the tenant router in the test DB layer — it returns None
# from get_current_db_name() unless middleware ran, which breaks pytest's
# test DB setup. We test the router directly in its unit tests.
DATABASE_ROUTERS = []

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

USE_TZ = True
TIME_ZONE = "Asia/Calcutta"
LANGUAGE_CODE = "en-us"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Paths the production settings expose — declared here so any code that reads
# them at import time still finds something.
REGISTERS_LOG = os.path.join(BASE_DIR, "tests", "_logs", "registers.log")
SCREENING_COMMITTEE_LOG = os.path.join(BASE_DIR, "tests", "_logs", "psc.log")
KEYS_ROOT = os.path.join(BASE_DIR, "tests", "_keys")
date_strftime_format = "%d-%b-%Y %H:%M:%S %p"
msg_format = "%(asctime)s :: %(levelname)s :: %(message)s"
SESSION_EXPIRE_SECONDS = 900
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = "/logout"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520

# Create directories so file handlers don't crash on import
os.makedirs(os.path.dirname(REGISTERS_LOG), exist_ok=True)
os.makedirs(os.path.dirname(SCREENING_COMMITTEE_LOG), exist_ok=True)
os.makedirs(KEYS_ROOT, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {"class": "logging.NullHandler"},
    },
    "root": {"handlers": ["null"], "level": "CRITICAL"},
}
