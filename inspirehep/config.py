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

# Assets configuration
SASS_BIN = 'node-sass'
REQUIREJS_CONFIG = 'js/build.js'

# Theme
THEME_SITENAME = _("inspirehep")

# Database
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://inspirehep:dbpass123@localhost:5432/inspirehep")
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


SEARCH_UI_BASE_TEMPLATE = 'inspirehep_theme/page.html'

RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            title=_('Best match'),
            fields=['_score'],
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            title=_('Most recent'),
            fields=['earliest_date'],
            default_order='desc',
            order=2,
        ),
    )
)

RECORDS_UI_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        route='/records/<pid_value>',
        template='inspirehep_theme/format/record/Inspire_Default_HTML_detailed.tpl'
    )
)

JSONSCHEMAS_HOST = "localhost:5000"
INDEXER_DEFAULT_INDEX = "records-hep"
INDEXER_DEFAULT_DOC_TYPE = "record"

# from invenio_records_rest.facets import terms_filter
# SEARCH_UI_SEARCH_API='/api/records/'
# SEARCH_UI_SEARCH_INDEX='hep'
# INDEXER_DEFAULT_INDEX='hep'
# INDEXER_DEFAULT_DOC_TYPE='record'
# RECORDS_REST_ENDPOINTS=dict(
#     recid=dict(
#         pid_type='recid',
#         pid_minter='recid_minter',
#         pid_fetcher='recid_fetcher',
#         search_index='testrecords',
#         search_type=None,
#         record_serializers={
#             'application/json': ('invenio_records_rest.serializers'
#                                  ':record_to_json_serializer'),
#         },
#         search_serializers={
#             'application/json': ('invenio_records_rest.serializers'
#                                  ':search_to_json_serializer'),
#         },
#         list_route='/records/',
#         item_route='/records/<pid_value>',
#         default_media_type='application/json'
#     ),
# )

# RECORDS_REST_FACETS=dict(
#     testrecords=dict(
#         aggs=dict(
#             authors=dict(terms=dict(
#                 field='added_entry_personal_name.personal_name')),
#             languages=dict(terms=dict(
#                 field='language_code.language_code_of_text_'
#                       'sound_track_or_separate_title')),
#             topic=dict(terms=dict(
#                 field='subject_added_entry_topical_term.'
#                       'topical_term_or_geographic_name_entry_element')),
#         ),
#         post_filters=dict(
#             authors=terms_filter(
#                 'added_entry_personal_name.personal_name'),
#             languages=terms_filter(
#                 'language_code.language_code_of_text_'
#                 'sound_track_or_separate_title'),
#             topic=terms_filter(
#                 'subject_added_entry_topical_term.'
#                 'topical_term_or_geographic_name_entry_element'),
#         )
#     )
# )

# RECORDS_REST_DEFAULT_SORT=dict(
#     testrecords=dict(query='-bestmatch', noquery='controlnumber'),
# )

# RECORDS_UI_DEFAULT_PERMISSION_FACTORY=None
