# -*- coding: utf-8 -*-

"""inspirehep base Invenio configuration."""

from __future__ import absolute_import, print_function

import os


# Identity function for string extraction
def _(x):
    return x

# Default language and timezone
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
I18N_LANGUAGES = [
]

BASE_TEMPLATE = "invenio_theme/page.html"
COVER_TEMPLATE = "invenio_theme/page_cover.html"
SETTINGS_TEMPLATE = "invenio_theme/settings/content.html"

# Theme
THEME_SITENAME = _("inspirehep")

# Database
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://localhost/hepdata")
SQLALCHEMY_ECHO = False

# Distributed task queue
BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND = "amqp://guest:guest@localhost:5672//"
CELERY_ACCEPT_CONTENT = ['msgpack']

# Needed for Celery beat to be scheduled correctly in our timezone
CELERY_TIMEZONE = 'Europe/Amsterdam'

# Performance boost as long as we do not use rate limits on tasks
CELERY_DISABLE_RATE_LIMITS = True

# Cache
CACHE_KEY_PREFIX = "cache::"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_TYPE = "redis"

# Session
SESSION_REDIS = "redis://localhost:6379/0"

# Accounts
RECAPTCHA_PUBLIC_KEY = "CHANGE_ME"
RECAPTCHA_SECRET_KEY = "CHANGE_ME"

# SECURITY_REGISTER_USER_TEMPLATE = \
#     "hepdata_theme/security/register_user.html"
# SECURITY_LOGIN_USER_TEMPLATE = \
#     "hepdata_theme/security/login_user.html"
# SECURITY_RESET_PASSWORD_TEMPLATE = \
#     "hepdata_theme/security/reset_password.html"

SECURITY_CONFIRM_SALT = "CHANGE_ME"
SECURITY_EMAIL_SENDER = "admin@inspirehep.net"
SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to INSPIRE Labs!")
SECURITY_LOGIN_SALT = "CHANGE_ME"
SECURITY_PASSWORD_SALT = "CHANGE_ME"
SECURITY_REMEMBER_SALT = "CHANGE_ME"
SECURITY_RESET_SALT = "CHANGE_ME"

# Theme
# THEME_SITENAME = _("HEPData")
# THEME_TWITTERHANDLE = "@hepdata"
# THEME_LOGO = "img/hepdata_logo.svg"
# THEME_GOOGLE_SITE_VERIFICATION = [
#     "5fPGCLllnWrvFxH9QWI0l1TadV7byeEvfPcyK2VkS_s",
#     "Rp5zp04IKW-s1IbpTOGB7Z6XY60oloZD5C3kTM-AiY4"
# ]

# BASE_TEMPLATE = "hepdata_theme/page.html"
# COVER_TEMPLATE = "hepdata_theme/page_cover.html"
# SETTINGS_TEMPLATE = "invenio_theme/page_settings.html"

# ELASTICSEARCH_INDEX = 'hepdata'
# SEARCH_ELASTIC_HOSTS = [
#     'localhost:9200'
# ]

SEARCH_AUTOINDEX = []
