# -*- coding: utf-8 -*-

"""inspirehep base Invenio configuration."""

from __future__ import absolute_import, print_function

import os


# Identity function for string extraction
def _(x):
    return x

SERVER_NAME = "localhost:5000"

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

SECURITY_LOGIN_USER_TEMPLATE = \
    "inspirehep_theme/accounts/login.html"
SECURITY_FORGOT_PASSWORD_TEMPLATE = \
    "inspirehep_theme/accounts/forgot_password.html"
SECURITY_RESET_PASSWORD_TEMPLATE = \
    "inspirehep_theme/accounts/reset_password.html"

SECURITY_CONFIRM_SALT = "CHANGE_ME"
SECURITY_EMAIL_SENDER = "admin@inspirehep.net"
SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to INSPIRE Labs!")
SECURITY_LOGIN_SALT = "CHANGE_ME"
SECURITY_PASSWORD_SALT = "CHANGE_ME"
SECURITY_REMEMBER_SALT = "CHANGE_ME"
SECURITY_RESET_SALT = "CHANGE_ME"


SEARCH_UI_BASE_TEMPLATE = 'inspirehep_theme/page.html'
USERPROFILES_SETTINGS_TEMPLATE = 'inspirehep_theme/accounts/settings/profile.html'

RECORDS_REST_ENDPOINTS = dict(
    literature=dict(
        pid_type='literature',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-hep',
        search_type='hep',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/literature/',
        item_route='/literature/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
    authors=dict(
        pid_type='authors',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-authors',
        search_type='authors',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/authors/',
        item_route='/authors/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
    data=dict(
        pid_type='data',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-data',
        search_type='data',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/data/',
        item_route='/data/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
    conferences=dict(
        pid_type='conferences',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-conferences',
        search_type='conferences',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/conferences/',
        item_route='/conferences/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
    jobs=dict(
        pid_type='jobs',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-jobs',
        search_type='jobs',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/jobs/',
        item_route='/jobs/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
    institutions=dict(
        pid_type='institutions',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-institutions',
        search_type='institutions',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/institutions/',
        item_route='/institutions/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
    experiments=dict(
        pid_type='experiments',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-experiments',
        search_type='experiments',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/experiments/',
        item_route='/experiments/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
    journals=dict(
        pid_type='journals',
        pid_minter='recid_minter',
        pid_fetcher='recid_fetcher',
        search_index='records-journals',
        search_type='journals',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':search_to_json_serializer'),
        },
        list_route='/journals/',
        item_route='/journals/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
    ),
)

RECORDS_UI_ENDPOINTS = dict(
    literature=dict(
        pid_type='literature',
        route='/literature/<pid_value>',
        template='inspirehep_theme/format/record/'
                 'Inspire_Default_HTML_detailed.tpl'
    ),
    authors=dict(
        pid_type='authors',
        route='/authors/<pid_value>',
        template='inspirehep_theme/format/record/Author_HTML_detailed.tpl'
    ),
    data=dict(
        pid_type='data',
        route='/data/<pid_value>',
        template='inspirehep_theme/format/record/Data_HTML_detailed.tpl'
    ),
    conferences=dict(
        pid_type='conferences',
        route='/conferences/<pid_value>',
        template='inspirehep_theme/format/record/Conference_HTML_detailed.tpl'
    ),
    jobs=dict(
        pid_type='jobs',
        route='/jobs/<pid_value>',
        template='inspirehep_theme/format/record/Job_HTML_detailed.tpl'
    ),
    institutions=dict(
        pid_type='institutions',
        route='/institutions/<pid_value>',
        template='inspirehep_theme/format/record/Institution_HTML_detailed.tpl'
    ),
    experiments=dict(
        pid_type='experiments',
        route='/experiments/<pid_value>',
        template='inspirehep_theme/format/record/Experiment_HTML_detailed.tpl'
    ),
    journals=dict(
        pid_type='journals',
        route='/journals/<pid_value>',
        template='inspirehep_theme/format/record/Journal_HTML_detailed.tpl'
    )
)

RECORDS_VALIDATION_TYPES = {
    'array': (list, tuple),
}

JSONSCHEMAS_HOST = "localhost:5000"
INDEXER_DEFAULT_INDEX = "records-hep"
INDEXER_DEFAULT_DOC_TYPE = "record"

# OAuthclient
OAUTHCLIENT_REMOTE_APPS = dict(
    orcid=dict(
        title='ORCID',
        description='Connecting Research and Researchers.',
        icon='',
        authorized_handler="invenio_oauthclient.handlers"
                           ":authorized_signup_handler",
        disconnect_handler="invenio_oauthclient.handlers"
                           ":disconnect_handler",
        signup_handler=dict(
            info="invenio_oauthclient.contrib.orcid:account_info",
            setup="invenio_oauthclient.contrib.orcid:account_setup",
            view="invenio_oauthclient.handlers:signup_handler",
        ),
        params=dict(
            request_token_params={'scope': '/authenticate'},
            base_url='https://pub.orcid.org/',
            request_token_url=None,
            access_token_url="https://pub.orcid.org/oauth/token",
            access_token_method='POST',
            authorize_url="https://orcid.org/oauth/authorize?show_login=true",
            app_key="OAUTHCLIENT_ORCID_CREDENTIALS",
            content_type="application/json",
        )
    ),
)

OAUTHCLIENT_ORCID_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

# Feedback
CFG_SITE_SUPPORT_EMAIL = "admin@inspirehep.net"
INSPIRELABS_FEEDBACK_EMAIL = "labsfeedback@inspirehep.net"

# ######################################################## #
# From here onwards is the backported search configuration #
# ######################################################## #

SEARCH_QUERY_PARSER = 'invenio_query_parser.contrib.spires.parser:Main'

SEARCH_QUERY_WALKERS = [
    'invenio_query_parser.contrib.spires.walkers.pypeg_to_ast:PypegConverter',
    'invenio_query_parser.contrib.spires.walkers.spires_to_invenio:SpiresToInvenio'
]

SEARCH_WALKERS = [
    'inspirehep.modules.search.walkers.elasticsearch:ElasticSearchDSL'
]

# SEARCH_ELASTIC_KEYWORD_MAPPING -- this variable holds a dictionary to map
# invenio keywords to elasticsearch fields
SEARCH_ELASTIC_KEYWORD_MAPPING = {
    None: ['global_fulltext'],
    "control_number": ["control_number"],
    "author": ["authors.full_name", "authors.alternative_name"],
    "exactauthor": ["exactauthor.raw", "authors.full_name",
                    "authors.alternative_name"
                    ],
    "abstract": ["abstracts.value"],
    "collaboration": ["collaboration.value", "collaboration.raw^2"],
    "collection": ["collections.primary"],
    "doi": ["dois.value"],
    "doc_type": ["facet_inspire_doc_type"],
    "formulas": ["facet_formulas"],
    "affiliation": ["authors.affiliations.value", "corporate_author"],
    "reportnumber": ["report_numbers.value", "arxiv_eprints.value"],
    "refersto": ["references.recid"],
    "experiment": ["accelerator_experiments.experiment"],
    "country": ["address.country", "address.country.raw"],
    "experiment_f": ["accelerator_experiments.facet_experiment"],
    "wwwlab": ["experiment_name.wwwlab"],
    "subject": ["field_code.value"],
    "phd_advisors": ["phd_advisors.name"],
    "title": ["titles.title", "titles.title.raw^2",
              "title_translation.title", "title_variation",
              "title_translation.subtitle", "titles.subtitle"],
    "cnum": ["publication_info.cnum"],
    "980": [
        "collections.primary",
        "collections.secondary",
        "collections.deleted",
    ],
    "595__c": ["hidden_notes.cds"],
    "980__a": ["collections.primary"],
    "980__b": ["collections.secondary"],
    "542__l": ["information_relating_to_copyright_status.copyright_status"],
    "conf_subject": ["field_code.value"],
    "037__c": ["arxiv_eprints.categories"],
    "246__a": ["titles.title"],
    "595": ["hidden_notes"],
    "650__a": ["subject_terms.term"],
    "695__a": ["thesaurus_terms.keyword"],
    "773__y": ["publication_info.year"],
    "authorcount": ["authors.full_name"],
    "arXiv": ["arxiv_eprints.value"],
    "caption": ["urls.description"],
    "country": ["authors.affiliations.value"],
    "firstauthor": ["authors.full_name", "authors.alternative_name"],
    "fulltext": ["urls.url"],
    "journal": ["publication_info.recid",
                "publication_info.page_artid",
                "publication_info.journal_issue",
                "publication_info.conf_acronym",
                "publication_info.journal_title",
                "publication_info.reportnumber",
                "publication_info.confpaper_info",
                "publication_info.journal_volume",
                "publication_info.cnum",
                "publication_info.pubinfo_freetext",
                "publication_info.year_raw",
                "publication_info.isbn",
                "publication_info.note"
                ],
    "journal_page": ["publication_info.page_artid"],
    "keyword": ["thesaurus_terms.keyword", "free_keywords.value"],
    "note": ["public_notes.value"],
    "reference": ["references.doi", "references.report_number",
                  "references.journal_pubnote"
                  ],
    "subject": ["subject_terms.term"],
    "texkey": ["external_system_numbers.value",
               "external_system_numbers.obsolete"
               ],
    "year": ["imprints.date",
             "preprint_date",
             "thesis.date",
             "publication_info.year"
             ],
    "confnumber": ["publication_info.cnum"],
    "earliest_date": ["earliest_date"],
    "address": ["corporate_author"],
    "datecreated": ["creation_modification_date.creation_date"],
    "datemodified": ["creation_modification_date.modification_date"],
    "recid": ["control_number"]
}

FACETS_SIZE_LIMIT = 10

SEARCH_ELASTIC_AGGREGATIONS = {
    "hep": {
        "subject": {
            "terms": {
                "field": "facet_inspire_subjects"
            }
        },
        "doc_type": {
            "terms": {
                "field": "facet_inspire_doc_type"
            }
        },
        "formulas": {
            "terms": {
                "field": "facet_formulas"
            }
        },
        "author": {
            "terms": {
                "field": "exactauthor.raw"
            }
        },
        "experiment": {
            "terms": {
                "field": "accelerator_experiments.facet_experiment"
            }
        },
        "earliest_date": {
            "date_histogram": {
                "field": "earliest_date",
                "interval": "year",
                "min_doc_count": 1
            }
        }
    },
    "conferences": {
        "series": {
            "terms": {
                "field": "series"
            }
        },
        "conf_subject": {
            "terms": {
                "field": "field_code.value"
            }
        },
        "opening_date": {
            "date_histogram": {
                "field": "opening_date",
                "interval": "year"
            }
        }
    },
    "experiments": {
        "field_code": {
            "terms": {
                "field": "field_code"
            }
        },
        "wwwlab": {
            "terms": {
                "field": "experiment_name.wwwlab"
            }
        },
        "accelerator": {
            "terms": {
                "field": "accelerator"
            }
        }
    },
    "journals": {
        "publisher": {
            "terms": {
                "field": "publisher"
            }
        }
    },
    "institutions": {
        "country": {
            "terms": {
                "field": "address.country.raw"
            }
        }
    },
    "jobs": {
        "continent": {
            "terms": {
                "field": "continent"
            }
        },
        "rank": {
            "terms": {
                "field": "rank"
            }
        },
        "research_area": {
            "terms": {
                "field": "research_area"
            }
        }
    }
}

# SEARCH_QUERY_ENHANCERS = ['invenio_search.enhancers.collection_filter.apply']
SEARCH_ELASTIC_SORT_FIELDS = ["earliest_date", "citation_count"]


SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING = {
    "hep": "records-hep",
    "cdf internal notes": "records-hep",
    "conferences": "records-conferences",
    "institutions": "records-institutions",
    "experiments": "records-experiments",
    "jobs": "records-jobs",
    "jobs hidden": "records-jobs",
    "journals": "records-journals",
    "hepnames": "records-authors",
    "data": "records-data"
}

# FIXME replace with invenio-search equal setting
SEARCH_ELASTIC_DEFAULT_INDEX = 'records-hep'
