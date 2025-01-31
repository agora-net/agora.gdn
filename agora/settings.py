"""
Django settings for agora project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import re
import sys
import tempfile
from pathlib import Path

import environ

PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = Path(__file__).resolve().parent.parent

TESTING = "test" in sys.argv

environ.Env.read_env(BASE_DIR / ".env")
environ.Env.read_env(BASE_DIR / ".env.local")

env = environ.Env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

DEBUG = env.bool("DEBUG", default=False)

SECRET_KEY = env.str("SECRET_KEY", default="!!!SET DJANGO_SECRET_KEY!!!")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=False)

INTERNAL_IPS = [
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    # The required `allauth` apps
    "allauth",
    "allauth.account",
    # Additional MFA
    "allauth.mfa",
    "home",
    "search",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_countries",
    "django_vite",
    "user",  # Custom user model
]

if DEBUG and not TESTING:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # By default, users have to be fully onboarded to do anything.
    # Whitelist views with `onboarding_required = False` to bypass this middleware.
    "user.middleware.FullyOnboardedUserRequiredMiddleware",
]

if DEBUG and not TESTING:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "agora.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
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

WSGI_APPLICATION = "agora.wsgi.application"

# Logging config
# https://docs.djangoproject.com/en/5.1/topics/logging/
# Taken from: https://www.reddit.com/r/django/comments/x2h6cq/whats_your_logging_setup/


LOG_LEVEL = env.str("LOG_LEVEL", default="WARNING")
LOGS_SAVE_TO_FILE = env.bool("LOGS_SAVE_TO_FILE", default=False)
LOGS_DIR = BASE_DIR / "logs"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "no_error_messages": {"()": "utils.log.NonErrorFilter"},
        "require_save_to_file": {"()": "utils.log.RequireSaveToFileFilter"},
    },
    "formatters": {
        "superverbose": {
            "format": (
                "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(process)d %(thread)d %(message)s"
            )
        },
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
        "json": {
            "()": "utils.log.JSONFormatter",
            "fmt_keys": {
                # key = value in the JSON log message output
                # value = logging variable that will be used
                "level": "levelname",
                "timestamp": "asctime",
                "msg": "message",
                "logger": "name",
                "pid": "process",
                "tid": "thread",
                "exception": "exc_info",
            },
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "debug_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "debug.log",
            "formatter": "json",
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 3,
            "encoding": "utf-8",
            "filters": ["require_save_to_file", "no_error_messages"],
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "error.log",
            "formatter": "json",
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 3,
            "encoding": "utf-8",
            "filters": ["require_save_to_file"],
        },
        "file_queue": {
            "level": "DEBUG",
            "class": "logging.handlers.QueueHandler",
            "handlers": ["debug_file", "error_file"],
            "respect_handler_level": True,
        },
        "email_queue": {
            "level": "ERROR",
            "class": "logging.handlers.QueueHandler",
            "handlers": ["mail_admins"],
            "respect_handler_level": True,
        },
    },
    "root": {"level": LOG_LEVEL, "handlers": ["console", "file_queue"]},
    "loggers": {
        "django.utils.autoreload": {
            "handlers": [],
            "level": "ERROR",
        },
        "django": {
            "handlers": [
                "console",
            ],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["email_queue"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "email_queue"],
            "propagate": True,
        },
    },
}

LOGGING_CONFIG = "utils.log.load_logging_config_start_listener"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": env.db_url("DB_DEFAULT_URL", "sqlite:///db.sqlite3"),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# For databases, if using SQLITE, add the following options
# https://gcollazo.com/optimal-sqlite-settings-for-django/
# https://briandouglas.ie/sqlite-defaults/
SQLITE_OPTIONS = {
    "init_command": (
        "PRAGMA foreign_keys = ON;"
        "PRAGMA journal_mode = WAL;"
        "PRAGMA synchronous = NORMAL;"
        "PRAGMA busy_timeout = 500;"  # 500ms
        "PRAGMA temp_store = MEMORY;"
        "PRAGMA auto_vacuum = INCREMENTAL;"
        f"PRAGMA page_size = {8 * 1024};"  # 8KB
        f"PRAGMA mmap_size = {128 * 1024 * 1024};"  # 128MB
        f"PRAGMA journal_size_limit = {64 * 1024 * 1024};"  # 64MB
        f"PRAGMA cache_size = -{20 * 1024 * 1024};"  # 20MB of 4096 bytes pages
    ),
    "transaction_mode": "IMMEDIATE",
}

# Cache
# https://docs.djangoproject.com/en/5.1/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "diskcache.DjangoCache",
        "LOCATION": env.str("CACHE_FILEPATH", tempfile.gettempdir()),
        "TIMEOUT": 300,
        # ^-- Django setting for default timeout of each key.
        "SHARDS": 8,
        "DATABASE_TIMEOUT": 0.010,  # 10 milliseconds
        # ^-- Timeout for each DjangoCache database transaction.
        "OPTIONS": {
            "size_limit": 2**30  # 1 gigabyte
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "user.password_validation.MaximumLengthValidator",
        "OPTIONS": {
            # As recommended by OWASP
            # https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#implement-proper-password-strength-controls
            "max_length": 64,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "utils.hashers.SecureArgon2PasswordHasher",
]

AUTH_USER_MODEL = "user.AgoraUser"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "account_login"
# todo(ewan): Update these to proper values
LOGIN_REDIRECT_URL = "profile"
LOGOUT_REDIRECT_URL = "/"

# All Auth
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_CHANGE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGIN_TIMEOUT = 60 * 15  # 15 minutes
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SIGNUP_FORM_HONEYPOT_FIELD = "user_name_required"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False

# All Auth MFA
# https://docs.allauth.org/en/latest/mfa/configuration.html
MFA_PASSKEY_LOGIN_ENABLED = False
MFA_PASSKEY_SIGNUP_ENABLED = False
MFA_TOTP_ISSUER = "Agora"
MFA_SUPPORTED_TYPES = ["recovery_codes", "totp"]
MFA_RECOVERY_CODE_COUNT = 12

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# Vite
# https://github.com/MrBin99/django-vite?tab=readme-ov-file#configuration-variables
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_protocol": "https",
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    PROJECT_DIR / "static",
    BASE_DIR / "frontend" / "@agora" / "agora" / "dist",
]

STATIC_ROOT = BASE_DIR / "static"
STATIC_HOST = env.str("STATIC_HOST", "")
STATIC_URL = STATIC_HOST + "/static/"

MEDIA_ROOT = env.str("MEDIA_ROOT", BASE_DIR / "media")
MEDIA_HOST = env.str("MEDIA_HOST", "")
MEDIA_URL = MEDIA_HOST + "/media/"

# Default storage settings, with the staticfiles storage updated.
# See https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-STORAGES
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    # ManifestStaticFilesStorage is recommended in production, to prevent
    # outdated JavaScript / CSS assets being served from cache
    # (e.g. after a Wagtail upgrade).
    # See https://docs.djangoproject.com/en/5.1/ref/contrib/staticfiles/#manifeststaticfilesstorage
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


vite_regex = re.compile(r"^.+[.-][0-9a-zA-Z_-]{8,12}\..+$")


def immutable_file_test(path: str, url: str) -> bool:
    # Match vite (rollup)-generated hashes, à la, `some_file-CSliV9zW.js`
    return bool(vite_regex.match(url))


# WhiteNoise settings
WHITENOISE_IMMUTABLE_FILE_TEST = immutable_file_test

# Taggit settings
# https://django-taggit.readthedocs.io/en/latest/getting_started.html#settings
TAGGIT_CASE_INSENSITIVE = True

# Wagtail settings

WAGTAIL_SITE_NAME = "agora"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = "https://agora.gdn"

# Allowed file extensions for documents in the document library.
# This can be omitted to allow all files, but note that this may present a security risk
# if untrusted users are allowed to upload files -
# see https://docs.wagtail.org/en/stable/advanced_topics/deploying.html#user-uploaded-files
WAGTAILDOCS_EXTENSIONS = [
    "csv",
    "docx",
    "key",
    "odt",
    "pdf",
    "pptx",
    "rtf",
    "txt",
    "xlsx",
    "zip",
]

# Debug toolbar settings
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
RESULTS_CACHE_SIZE = 100

# Agora settings
# ------------------------------------

# Which routes do not require the user to be fully onboarded?
# Each of these can be an explicit path or a URL name.
AGORA_ONBOARDING_NOT_REQUIRED_ROUTES = [
    # Allauth
    "account_login",
    "account_signup",
    "account_signup_by_passkey",
    "account_confirm_email",
    "account_email_verification_sent",
    "account_reauthenticate",
    "account_reset_password",
    "account_reset_password_done",
    "account_reset_password_from_key",
    "account_reset_password_from_key_done",
    "mfa_index",
    "mfa_authenticate",
    "mfa_reauthenticate",
    "mfa_activate_totp",
    "mfa_view_recovery_codes",
    "mfa_generate_recovery_codes",
    "mfa_download_recovery_codes",
]

if DEBUG:
    AGORA_ONBOARDING_NOT_REQUIRED_ROUTES += ["/__debug__/"]

for db in DATABASES.values():
    if "sqlite3" in db["ENGINE"]:
        options = SQLITE_OPTIONS.copy()
        options.update(db.get("OPTIONS", {}))
        db["OPTIONS"] = options
