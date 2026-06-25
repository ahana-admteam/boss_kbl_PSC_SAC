######   Local settings   #####

DEBUG = True
AD_LOGIN = False

ALLOWED_HOSTS = ["kotak.localhost", "localhost","fincare.localhost", "hdfc.localhost", "jana.localhost", "rbl.localhost", "fincare.13.68.238.3", ".fincare.13.68.238.3", "13.68.238.3", "demo.localhost", "ujjivan.localhost", "svc.localhost"]

DATABASES = {
   "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "kotak": {"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "jana": {"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "fincare": {"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "hdfc": {"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "rbl": {"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "demo":{"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "ujjivan":{"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"},
   "svc":{"ENGINE": "django.db.backends.sqlite3", "NAME": "default.db.sqlite3"}

}

