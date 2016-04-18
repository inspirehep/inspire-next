# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""INSPIREHep default application configuration."""

from __future__ import absolute_import, print_function

import os

from invenio_records_rest.facets import terms_filter


def _(x):
    """Identity function for string extraction."""
    return x


# Debug
# =====
DEBUG_TB_INTERCEPT_REDIRECTS = False
SERVER_NAME = "localhost:5000"

# Default language and timezone
# =============================
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Amsterdam'
I18N_LANGUAGES = []

# Assets configuration
# ====================
SASS_BIN = 'node-sass'
REQUIREJS_CONFIG = 'js/build.js'

# Theme
# =====
THEME_SITENAME = "HEP"

# Database
# ========
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://inspirehep:dbpass123@localhost:5432/inspirehep")
SQLALCHEMY_ECHO = False

# Celery
# ======
BROKER_URL = os.environ.get(
    "BROKER_URL",
    "amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND",
    "amqp://guest:guest@localhost:5672//")
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TIMEZONE = 'Europe/Amsterdam'
CELERY_DISABLE_RATE_LIMITS = True

# Cache
# =====
CACHE_KEY_PREFIX = "cache::"
CACHE_REDIS_URL = os.environ.get(
    "CACHE_REDIS_URL",
    "redis://localhost:6379/0")
CACHE_TYPE = "redis"
ACCOUNTS_SESSION_REDIS_URL = "redis://localhost:6379/2"

# REST
# ====
REST_ENABLE_CORS = True

# Accounts
# ========
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

REMEMBER_COOKIE_HTTPONLY = True
"""
Prevents the "Remember Me" cookie from being accessed by client-side
scripts
"""
# User profile
# ============
# FIXME Investigate why setting this to True sometimes forces using
# the flask_security extension before being correctly initialized.
USERPROFILES_EXTEND_SECURITY_FORMS = False
USERPROFILES_SETTINGS_TEMPLATE = 'inspirehep_theme/accounts/settings/profile.html'

# Search
# ======
SEARCH_ELASTIC_HOSTS = os.environ.get(
    'SEARCH_ELASTIC_HOSTS',
    'localhost').split(';')
SEARCH_UI_BASE_TEMPLATE = 'inspirehep_theme/page.html'
SEARCH_UI_SEARCH_TEMPLATE = 'search/search.html'
SEARCH_UI_SEARCH_API = '/api/literature/'
SEARCH_UI_SEARCH_INDEX = 'records-hep'

SEARCH_QUERY_PARSER = 'invenio_query_parser.contrib.spires.parser:Main'

SEARCH_QUERY_WALKERS = [
    'invenio_query_parser.contrib.spires.walkers.pypeg_to_ast:PypegConverter',
    'invenio_query_parser.contrib.spires.walkers.spires_to_invenio:SpiresToInvenio'
]

SEARCH_WALKERS = [
    'inspirehep.modules.search.walkers.elasticsearch:ElasticSearchDSL'
]

SEARCH_QUERY_ENHANCERS = [
    'invenio_collections.contrib.search.collection_filter.apply'
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
    "tc": ["collection"],
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
    "fc": ["field_code"],
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
    "arxiv": ["arxiv_eprints.value"],
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
    "recid": ["control_number"],
    "cited": ["citation_count"],
    "topcite": ["citation_count"]
}

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

COLLECTIONS_USE_PERCOLATOR = True
""" Use Elasticsearch to match a document against a collection query """

# Records
# =======
RECORDS_REST_ENDPOINTS = dict(
    literature=dict(
        pid_type='literature',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-hep',
        search_type='hep',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/literature/',
        item_route='/literature/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
    ),
    authors=dict(
        pid_type='authors',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-authors',
        search_type='authors',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/authors/',
        item_route='/authors/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
    ),
    data=dict(
        pid_type='data',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-data',
        search_type='data',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/data/',
        item_route='/data/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
    ),
    conferences=dict(
        pid_type='conferences',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-conferences',
        search_type='conferences',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/conferences/',
        item_route='/conferences/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
    ),
    jobs=dict(
        pid_type='jobs',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-jobs',
        search_type='jobs',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/jobs/',
        item_route='/jobs/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
    ),
    institutions=dict(
        pid_type='institutions',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-institutions',
        search_type='institutions',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/institutions/',
        item_route='/institutions/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
    ),
    experiments=dict(
        pid_type='experiments',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-experiments',
        search_type='experiments',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/experiments/',
        item_route='/experiments/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
    ),
    journals=dict(
        pid_type='journals',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_index='records-journals',
        search_type='journals',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_brief_v1_search'
            ),
        },
        list_route='/journals/',
        item_route='/journals/<pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        query_factory_imp='inspirehep.modules.search.query:inspire_query_factory',
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

RECORDS_REST_FACETS = {
    "records-hep": {
        "filters": {
            "author": terms_filter('exactauthor.raw'),
            "subject": terms_filter('facet_inspire_subjects'),
            "doc_type": terms_filter('facet_inspire_doc_type'),
            "formulas": terms_filter('facet_formulas'),
            "experiment": terms_filter('accelerator_experiments.facet_experiment'),
        },
        "aggs": {
            "subject": {
                "terms": {
                    "field": "facet_inspire_subjects",
                    "size": 20
                }
            },
            "doc_type": {
                "terms": {
                    "field": "facet_inspire_doc_type",
                    "size": 20
                }
            },
            "formulas": {
                "terms": {
                    "field": "facet_formulas",
                    "size": 20
                }
            },
            "author": {
                "terms": {
                    "field": "exactauthor.raw",
                    "size": 20
                }
            },
            "experiment": {
                "terms": {
                    "field": "accelerator_experiments.facet_experiment",
                    "size": 20
                }
            },
            "earliest_date": {
                "date_histogram": {
                    "field": "earliest_date",
                    "interval": "year",
                    "min_doc_count": 1,
                    "order": {"_count": "desc"}
                }
            }
        }
    },
    "records-conferences": {
        "filters": {
            "series": terms_filter('series'),
            "conf_subject": terms_filter('field_code.value')
        },
        "aggs": {
            "series": {
                "terms": {
                    "field": "series",
                    "size": 20
                }
            },
            "conf_subject": {
                "terms": {
                    "field": "field_code.value",
                    "size": 20
                }
            },
            "opening_date": {
                "date_histogram": {
                    "field": "opening_date",
                    "interval": "year",
                    "min_doc_count": 1,
                    "order": {"_count": "desc"}
                }
            }
        }
    },
    "records-experiments": {
        "filters": {
            "field_code": terms_filter('field_code'),
            "wwwlab": terms_filter('experiment_name.wwwlab'),
            "accelerator": terms_filter('accelerator')
        },
        "aggs": {
            "field_code": {
                "terms": {
                    "field": "field_code",
                    "size": 20
                }
            },
            "wwwlab": {
                "terms": {
                    "field": "experiment_name.wwwlab",
                    "size": 20
                }
            },
            "accelerator": {
                "terms": {
                    "field": "accelerator",
                    "size": 20
                }
            }
        }
    },
    "records-journals": {
        "filters": {
            "publisher": terms_filter('publisher')
        },
        "aggs": {
            "publisher": {
                "terms": {
                    "field": "publisher",
                    "size": 20
                }
            }
        }
    },
    "records-institutions": {
        "filters": {
            "country": terms_filter('address.country.raw')
        },
        "aggs": {
            "country": {
                "terms": {
                    "field": "address.country.raw",
                    "size": 20
                }
            }
        }
    },
    "records-jobs": {
        "filters": {
            "continent": terms_filter('continent'),
            "rank": terms_filter('rank'),
            "research_area": terms_filter('research_area')
        },
        "aggs": {
            "continent": {
                "terms": {
                    "field": "continent",
                    "size": 20
                }
            },
            "rank": {
                "terms": {
                    "field": "rank",
                    "size": 20
                }
            },
            "research_area": {
                "terms": {
                    "field": "research_area",
                    "size": 20
                }
            }
        }
    }
}


RECORDS_REST_SORT_OPTIONS = {
    "records-hep": {
        "bestmatch": {
            "title": 'Best match',
            "fields": ['_score'],
            "default_order": 'desc',  # Used for invenio-search-js config
            "order": 1,
        },
        "mostrecent": {
            "title": 'Most recent',
            "fields": ['earliest_date'],
            "default_order": 'desc',  # Used for invenio-search-js config
            "order": 2,
        },
        "mostcited": {
            "title": 'Most cited',
            "fields": ['citation_count'],
            "default_order": 'desc',  # Used for invenio-search-js config
            "order": 3,
        },
    },
}

RECORDS_REST_DEFAULT_SORT = {
    "records-hep": {
        "query": "-bestmatch",
        "noquery": "-mostrecent"
    }
}

RECORDS_VALIDATION_TYPES = {
    'array': (list, tuple),
}

JSONSCHEMAS_HOST = "localhost:5000"
INDEXER_DEFAULT_INDEX = "records-hep"
INDEXER_DEFAULT_DOC_TYPE = "hep"

# OAuthclient
# ===========
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
# ========
CFG_SITE_SUPPORT_EMAIL = "admin@inspirehep.net"
INSPIRELABS_FEEDBACK_EMAIL = "labsfeedback@inspirehep.net"

# Submission
# ==========
CFG_ROBOTUPLOAD_SUBMISSION_BASEURL = "http://localhost:5000"

# Inspire subject translation
# ===========================
ARXIV_TO_INSPIRE_CATEGORY_MAPPING = {
    'alg-geom': 'Math and Math Physics',
    'astro-ph': 'Astrophysics',
    'astro-ph.CO': 'Astrophysics',
    'astro-ph.EP': 'Astrophysics',
    'astro-ph.GA': 'Astrophysics',
    'astro-ph.HE': 'Astrophysics',
    'astro-ph.IM': 'Instrumentation',
    'astro-ph.SR': 'Astrophysics',
    'cond-mat': 'General Physics',
    'cond-mat.dis-nn': 'General Physics',
    'cond-mat.mes-hall': 'General Physics',
    'cond-mat.mtrl-sci': 'General Physics',
    'cond-mat.other': 'General Physics',
    'cond-mat.quant-gas': 'General Physics',
    'cond-mat.soft': 'General Physics',
    'cond-mat.stat-mech': 'General Physics',
    'cond-mat.str-el': 'General Physics',
    'cond-mat.supr-con': 'General Physics',
    'cs': 'Computing',
    'cs.AI': 'Computing',
    'cs.AR': 'Computing',
    'cs.CC': 'Computing',
    'cs.CE': 'Computing',
    'cs.CG': 'Computing',
    'cs.CL': 'Computing',
    'cs.CR': 'Computing',
    'cs.CV': 'Computing',
    'cs.CY': 'Computing',
    'cs.DB': 'Computing',
    'cs.DC': 'Computing',
    'cs.DL': 'Computing',
    'cs.DM': 'Computing',
    'cs.DS': 'Computing',
    'cs.ET': 'Computing',
    'cs.FL': 'Computing',
    'cs.GL': 'Computing',
    'cs.GR': 'Computing',
    'cs.GT': 'Computing',
    'cs.HC': 'Computing',
    'cs.IR': 'Computing',
    'cs.IT': 'Computing',
    'cs.LG': 'Computing',
    'cs.LO': 'Computing',
    'cs.MA': 'Computing',
    'cs.MM': 'Computing',
    'cs.MS': 'Computing',
    'cs.NA': 'Computing',
    'cs.NE': 'Computing',
    'cs.NI': 'Computing',
    'cs.OH': 'Computing',
    'cs.OS': 'Computing',
    'cs.PF': 'Computing',
    'cs.PL': 'Computing',
    'cs.RO': 'Computing',
    'cs.SC': 'Computing',
    'cs.SD': 'Computing',
    'cs.SE': 'Computing',
    'cs.SI': 'Computing',
    'cs.SY': 'Computing',
    'dg-ga': 'Math and Math Physics',
    'gr-qc': 'Gravitation and Cosmology',
    'hep-ex': 'Experiment-HEP',
    'hep-lat': 'Lattice',
    'hep-ph': 'Phenomenology-HEP',
    'hep-th': 'Theory-HEP',
    'math': 'Math and Math Physics',
    'math-ph': 'Math and Math Physics',
    'math.AC': 'Math and Math Physics',
    'math.AG': 'Math and Math Physics',
    'math.AP': 'Math and Math Physics',
    'math.AT': 'Math and Math Physics',
    'math.CA': 'Math and Math Physics',
    'math.CO': 'Math and Math Physics',
    'math.CT': 'Math and Math Physics',
    'math.CV': 'Math and Math Physics',
    'math.DG': 'Math and Math Physics',
    'math.DS': 'Math and Math Physics',
    'math.FA': 'Math and Math Physics',
    'math.GM': 'Math and Math Physics',
    'math.GN': 'Math and Math Physics',
    'math.GR': 'Math and Math Physics',
    'math.GT': 'Math and Math Physics',
    'math.HO': 'Math and Math Physics',
    'math.IT': 'Math and Math Physics',
    'math.KT': 'Math and Math Physics',
    'math.LO': 'Math and Math Physics',
    'math.MG': 'Math and Math Physics',
    'math.MP': 'Math and Math Physics',
    'math.NA': 'Math and Math Physics',
    'math.NT': 'Math and Math Physics',
    'math.OA': 'Math and Math Physics',
    'math.OC': 'Math and Math Physics',
    'math.PR': 'Math and Math Physics',
    'math.QA': 'Math and Math Physics',
    'math.RA': 'Math and Math Physics',
    'math.RT': 'Math and Math Physics',
    'math.SG': 'Math and Math Physics',
    'math.SP': 'Math and Math Physics',
    'math.ST': 'Math and Math Physics',
    'nlin': 'General Physics',
    'nlin.AO': 'General Physics',
    'nlin.CD': 'General Physics',
    'nlin.CG': 'General Physics',
    'nlin.PS': 'Math and Math Physics',
    'nlin.SI': 'Math and Math Physics',
    'nucl-ex': 'Experiment-Nucl',
    'nucl-th': 'Theory-Nucl',
    'patt-sol': 'Math and Math Physics',
    'physics': 'General Physics',
    'physics.acc-ph': 'Accelerators',
    'physics.ao-ph': 'General Physics',
    'physics.atm-clus': 'General Physics',
    'physics.atom-ph': 'General Physics',
    'physics.bio-ph': 'Other',
    'physics.chem-ph': 'Other',
    'physics.class-ph': 'General Physics',
    'physics.comp-ph': 'Computing',
    'physics.data-an': 'Computing',
    'physics.ed-ph': 'Other',
    'physics.flu-dyn': 'General Physics',
    'physics.gen-ph': 'General Physics',
    'physics.geo-ph': 'General Physics',
    'physics.hist-ph': 'Other',
    'physics.ins-det': 'Instrumentation',
    'physics.med-ph': 'Other',
    'physics.optics': 'General Physics',
    'physics.plasm-ph': 'General Physics',
    'physics.pop-ph': 'Other',
    'physics.soc-ph': 'Other',
    'physics.space-ph': 'Astrophysics',
    'q-alg': 'Math and Math Physics',
    'q-bio.BM': 'Other',
    'q-bio.CB': 'Other',
    'q-bio.GN': 'Other',
    'q-bio.MN': 'Other',
    'q-bio.NC': 'Other',
    'q-bio.OT': 'Other',
    'q-bio.PE': 'Other',
    'q-bio.QM': 'Other',
    'q-bio.SC': 'Other',
    'q-bio.TO': 'Other',
    'q-fin.CP': 'Other',
    'q-fin.EC': 'Other',
    'q-fin.GN': 'Other',
    'q-fin.MF': 'Other',
    'q-fin.PM': 'Other',
    'q-fin.PR': 'Other',
    'q-fin.RM': 'Other',
    'q-fin.ST': 'Other',
    'q-fin.TR': 'Other',
    'quant-ph': 'General Physics',
    'solv-int': 'Math and Math Physics',
    'stat.AP': 'Other',
    'stat.CO': 'Other',
    'stat.ME': 'Other',
    'stat.ML': 'Other',
    'stat.OT': 'Other',
    'stat.TH': 'Other'
}
