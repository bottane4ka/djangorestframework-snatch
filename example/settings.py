import os
import configparser

config_file = (
    os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))) + "/env.ini"
)
config = configparser.ConfigParser()
config.read(config_file)

SECRET_KEY = config["DJANGO"]["DJANGO_SECRET_KEY"]

DEBUG = True

ALLOWED_HOSTS = "*"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "manager",
    "snatch",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

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
            ]
        },
    }
]

WSGI_APPLICATION = "wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "OPTIONS": {"options": "-c search_path=manager,public"},
        "NAME": config["DATABASE"]["NAME"],
        "USER": config["DATABASE"]["USER"],
        "HOST": config["DATABASE"]["HOST"],
        "PORT": config["DATABASE"]["PORT"],
    }
}

SNATCH_FRAMEWORK = {"PAGE_SIZE": 20}

LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Moscow"
USE_TZ = True

STATIC_URL = "/static/"
