######  Prod settings #########

# print('reading prod file')
DEBUG = True
AD_LOGIN = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
    "NAME":"postgres",
    "ENGINE": "django.db.backends.postgresql",
    "OPTIONS": {
        'options': '-c search_path=cbcadm'
    },
    "USER": "screeningusr",
    "PASSWORD": "ScreeningUsr@123",
    "HOST": "172.16.224.240",
    "PORT": "5945"
    }
}

EXPLORER_CONNECTIONS = {"default":'default'}
