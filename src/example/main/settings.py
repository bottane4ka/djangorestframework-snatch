from pathlib import Path
import environ
import structlog
from labelgun.integrations.structlog_utils import (
    convert_event_dict_to_str_processor,
    dict_msg_processor,
)


def get_host(host_value):
    return "127.0.0.1" if LOCAL_MODE else host_value


env = environ.Env()
BASE_DIR = environ.Path(__file__) - 1
BASE_ROOT_DIR = BASE_DIR - 1

env.read_env(str(BASE_ROOT_DIR.path(".env")))

LOCAL_MODE = env.bool("LOCAL_MODE", default=True)
LOG_MOD = env.str("LOG_MOD", default="simple")
CURRENT_ENV = env.str("CURRENT_ENV", default="dev")

SECRET_KEY = env.str("DJANGO_SECRET_KEY")
DEBUG = True if CURRENT_ENV == "dev" else False
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest.manager",
    "rest.brave_rest_framework",
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

ROOT_URLCONF = "rest.main.urls"

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

WSGI_APPLICATION = "rest.main.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "OPTIONS": {"options": "-c search_path=manager,public"},
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "HOST": get_host(env.str("POSTGRES_HOST")),
        "PORT": env.int("POSTGRES_PORT", default=5432),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("rest_framework_filters.backends.RestFrameworkFilterBackend",),
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DATETIME_FORMAT": "%d-%m-%Y %H:%M",
    "DATETIME_INPUT_FORMATS": ["%d-%m-%Y %H:%M"],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}



LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


if LOG_MOD == "json":
    structlog_processors = [
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.format_exc_info,
        convert_event_dict_to_str_processor,
        dict_msg_processor,
    ]
    default_formatter = {
        "()": "labelgun.integrations.logging_utils.StructlogJsonFormatter",
        "json_ensure_ascii": False,
        "proc": structlog_processors,
    }
else:
    structlog_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ]
    default_formatter = {"format": "%(message)s"}

# structlog.configure(
#     processors=structlog_processors,
#     context_class=structlog.threadlocal.wrap_dict(dict),
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.stdlib.BoundLogger,
#     cache_logger_on_first_use=True,
# )

LOGGING = {
    "version": 1,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "default_formatter": default_formatter,
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(pathname)s %(funcName)s %(lineno)d %(process)d %(thread)d %(message)s",
            "datefmt": "%d/%m/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default_formatter",
            "filters": ["require_debug_true"],
        }
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        # "django.db.backends": {"handlers": ["console"], "level": "DEBUG"}
    },
}

MANAGER_SYSTEM_NAME = env.str("MANAGER_SYSTEM_NAME")
PERIOD_TIME = env.int("PERIOD_TIME", 3000)
LISTEN_MESSAGE_TABLE = env.str("LISTEN_MESSAGE_TABLE")
LISTEN_MAIN_TASK_TABLE = env.str("LISTEN_MAIN_TASK_TABLE")
LISTEN_TASK_TABLE = env.str("LISTEN_TASK_TABLE")
LISTEN_COMMAND_TABLE = env.str("LISTEN_COMMAND_TABLE")

TEST_RUNNER = 'tests.runner.PostgresSchemaTestRunner'
