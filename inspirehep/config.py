# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""INSPIREHEP app configuration."""

from __future__ import absolute_import, division, print_function
from logging.config import dictConfig

import os
import sys
import pkg_resources

from celery.schedules import crontab

from invenio_oauthclient.contrib import orcid
from invenio_records_rest.facets import range_filter, terms_filter
from invenio_records_rest.utils import allow_all

from .modules.records.facets import range_author_count_filter, must_match_all_filter
from .modules.search.facets import hep_author_publications

# Debug
# =====
DEBUG_TB_INTERCEPT_REDIRECTS = False
SERVER_NAME = 'localhost:5000'

# Feature flags
# =============
FEATURE_FLAG_ENABLE_ORCID_PUSH = False
# Only push to ORCIDs that match this regex.
# Examples:
#   any ORCID -> ".*"
#   none -> "^$"
#   some ORCIDs -> "^(0000-0002-7638-5686|0000-0002-7638-5687)$"
FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX = '.*'
FEATURE_FLAG_ENABLE_MERGER = True
FEATURE_FLAG_ENABLE_UPDATE_TO_LEGACY = False
FEATURE_FLAG_ENABLE_SEND_TO_LEGACY = True
"""This feature flag will prevent to send a ``replace`` update to legacy."""
FEATURE_FLAG_USE_ROOT_TABLE_ON_HEP = False
FEATURE_FLAG_ENABLE_SNOW = False
FEATURE_FLAG_ENABLE_SAVE_WORFLOW_ON_DOWNLOAD_DOCUMENTS = True
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
INSPIRE_FULL_THEME = True
"""Allows to switch between labs.inspirehep.net view and full version."""
THEME_SITENAME = "inspirehep"
BASE_TEMPLATE = "inspirehep_theme/page.html"

# Database
# ========
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://inspirehep:inspirehep@localhost:5432/inspirehep"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Celery
# ======
CELERY_BROKER_URL = "pyamqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
# Default UTC timezone for celery because of https://github.com/inveniosoftware/invenio-celery/issues/53
# CELERY_TIMEZONE = 'Europe/Amsterdam'
CELERY_WORKER_DISABLE_RATE_LIMITS = True
CELERY_BEAT_SCHEDULE = {
    'journal_kb_builder': {
        'task': 'inspirehep.modules.refextract.tasks.create_journal_kb_file',
        'schedule': crontab(minute='0', hour='*/1'),
    }
}

# GROBID
# ======
GROBID_URL = "http://SET_ME/"

# Cache
# =====
CACHE_KEY_PREFIX = "cache::"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_TYPE = "redis"
ACCOUNTS_SESSION_REDIS_URL = "redis://localhost:6379/2"
ACCESS_CACHE = "invenio_cache:current_cache"
RT_USERS_CACHE_TIMEOUT = 86400
RT_QUEUES_CACHE_TIMEOUT = 86400

# Files
# =====
BASE_FILES_LOCATION = os.path.join(sys.prefix, 'var/data')

# This is needed in order to be able to use EOS files locations
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB

FILES_REST_PERMISSION_FACTORY = allow_all
DOWNLOAD_FILE_TO_WORKFLOW_TIMEOUT = 300

# REST
# ====
REST_ENABLE_CORS = True
OAUTH2SERVER_ALLOWED_URLENCODE_CHARACTERS = '=&;:%+~,*@!()/? '

# Accounts
# ========
DANGEROUSLY_ENABLE_LOCAL_LOGIN = False

RECAPTCHA_PUBLIC_KEY = "CHANGE_ME"
RECAPTCHA_SECRET_KEY = "CHANGE_ME"

SECURITY_LOGIN_USER_TEMPLATE = "inspirehep_theme/accounts/login.html"
SECURITY_FORGOT_PASSWORD_TEMPLATE = "inspirehep_theme/accounts/forgot_password.html"
SECURITY_RESET_PASSWORD_TEMPLATE = "inspirehep_theme/accounts/reset_password.html"

SECURITY_CONFIRM_SALT = "CHANGE_ME"
SECURITY_EMAIL_SENDER = "admin@inspirehep.net"
SECURITY_EMAIL_SUBJECT_REGISTER = "Welcome to INSPIRE!"
SECURITY_LOGIN_SALT = "CHANGE_ME"
SECURITY_PASSWORD_SALT = "CHANGE_ME"
SECURITY_REMEMBER_SALT = "CHANGE_ME"
SECURITY_RESET_SALT = "CHANGE_ME"
SECURITY_PASSWORD_SCHEMES = [
    'pbkdf2_sha512',
    'sha512_crypt',
    'invenio_aes_encrypted_email'
]
SECURITY_DEPRECATED_PASSWORD_SCHEMES = [
    'sha512_crypt',
    'invenio_aes_encrypted_email'
]

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

# Collections
# ===========
COLLECTIONS_DELETED_RECORDS = '{dbquery} AND NOT deleted:True'
"""Enhance collection query to exclude deleted records."""

COLLECTIONS_USE_PERCOLATOR = False
"""Define which percolator you want to use.

Default value is `False` to use the internal percolator.
You can also set True to use ElasticSearch to provide percolator resolver.
NOTE that ES percolator uses high memory and there might be some problems
when creating records.
"""

COLLECTIONS_REGISTER_RECORD_SIGNALS = False
"""Don't register the signals when instantiating the extension.

Since we are instantiating the `invenio-collections` extension two times
we don't want to register the signals twice, but we want to explicitly
call `register_signals()` on our own.
"""

RECORD_EDITOR_FILE_UPLOAD_FOLDER = 'inspirehep/modules/editor/temp'

# Path to where journal kb file is stored from `inspirehep.modules.refextract.tasks.create_journal_kb_file`
# On production, if you enable celery beat change this path to point to a shared space.
REFEXTRACT_JOURNAL_KB_PATH = pkg_resources.resource_filename(
    'refextract', 'references/kbs/journal-titles.kb')

# Search
# ======

# Search Typeahead configuration

SEARCH_TYPEAHEAD_INVENIO_KEYWORDS = ['author', 'title']
SEARCH_TYPEAHEAD_SPIRES_KEYWORDS = ['a', 't', 'eprint', 'j']
SEARCH_TYPEAHEAD_INVENIO_KEYWORD_TO_HINT = {
    'author': 'authors.name_suggest'
}
SEARCH_TYPEAHEAD_SPIRES_KEYWORD_TO_HINT = {
    'a': 'authors.name_suggest'
}
SEARCH_TYPEAHEAD_HINT_URL = '/search/suggest?field=%TYPE&query=%QUERY'
SEARCH_TYPEAHEAD_DEFAULT_SET = 'invenio'

SEARCH_ELASTIC_HOSTS = ['localhost']
SEARCH_UI_BASE_TEMPLATE = BASE_TEMPLATE
SEARCH_UI_SEARCH_TEMPLATE = 'search/search.html'
SEARCH_UI_SEARCH_API = '/api/literature/'
SEARCH_UI_SEARCH_INDEX = 'records-hep'
INSPIRE_ENDPOINT_TO_INDEX = {
    'authors': 'records-authors',
    'conferences': 'records-conferences',
    'experiments': 'records-experiments',
    'institutions': 'records-institutions',
    'jobs': 'records-jobs',
    'journals': 'records-journals',
    'literature': 'records-hep',
}

# Records
# =======
INSPIRE_SERIALIZERS = 'inspirehep.modules.records.serializers'

LITERATURE_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'lit',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:LiteratureSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
        'application/vnd+inspire.record.ui+json': INSPIRE_SERIALIZERS + ':json_literature_ui_v1_response',
        'application/x-bibtex': INSPIRE_SERIALIZERS + ':bibtex_v1_response',
        'application/vnd+inspire.latex.eu+x-latex': INSPIRE_SERIALIZERS + ':latex_v1_response_eu',
        'application/vnd+inspire.latex.us+x-latex': INSPIRE_SERIALIZERS + ':latex_v1_response_us',
        'application/marcxml+xml': INSPIRE_SERIALIZERS + ':marcxml_v1_response',
    },
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
        'application/vnd+inspire.record.ui+json': INSPIRE_SERIALIZERS + ':json_literature_ui_v1_search_response',
        'application/x-bibtex': INSPIRE_SERIALIZERS + ':bibtex_v1_search',
        'application/vnd+inspire.ids+json': 'inspirehep.modules.api.v1.common_serializers:json_recids_response',
        'application/vnd+inspire.latex.eu+x-latex': INSPIRE_SERIALIZERS + ':latex_v1_search_eu',
        'application/vnd+inspire.latex.us+x-latex': INSPIRE_SERIALIZERS + ':latex_v1_search_us',
        'application/marcxml+xml': INSPIRE_SERIALIZERS + ':marcxml_v1_search',
    },
    'suggesters': {
        'abstract_source': {
            'completion': {
                'field': 'abstracts.abstract_source_suggest',
            },
        },
        'book_title': {
            '_source': [
                'control_number',
                'self',
                'titles',
                'authors',
            ],
            'completion': {
                'field': 'bookautocomplete'
            }
        }
    },
    'list_route': '/literature/',
    'item_route': '/literature/<pid(lit,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'read_permission_factory_imp': "inspirehep.modules.records.permissions:record_read_permission_factory",
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
}

LITERATURE_REFERENCES_REST_ENDPOINT = {
    'pid_type': 'lit',
    'search_class': 'inspirehep.modules.search:LiteratureSearch',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'record_serializers': {
        'application/json': 'inspirehep.modules.records.serializers:json_literature_references_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'inspirehep.modules.records.serializers:json_literature_references_v1_search',
    },
    'list_route': '/literature/references',
    'item_route': '/literature/<pid(lit,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/references',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'read_permission_factory_imp': "inspirehep.modules.records.permissions:record_read_permission_factory",
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

LITERATURE_AUTHORS_REST_ENDPOINT = {
    'pid_type': 'lit',
    'search_class': 'inspirehep.modules.search:LiteratureSearch',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'record_serializers': {
        'application/json': 'inspirehep.modules.records.serializers:json_literature_authors_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'inspirehep.modules.records.serializers:json_literature_authors_v1_search',
    },
    'list_route': '/literature/authors',
    'item_route': '/literature/<pid(lit,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/authors',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'read_permission_factory_imp': "inspirehep.modules.records.permissions:record_read_permission_factory",
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

AUTHORS_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'aut',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:AuthorsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
        'application/vnd+inspire.record.ui+json': INSPIRE_SERIALIZERS + ':json_authors_ui_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
        'application/vnd+inspire.ids+json': 'inspirehep.modules.api.v1.common_serializers:json_recids_response',
        'application/vnd+inspire.record.ui+json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'suggesters': {
        'author': {
            '_source': [
                'name',
                'control_number',
                'self',
            ],
            'completion': {
                'field': 'author_suggest',
            },
        }
    },
    'list_route': '/authors/',
    'item_route': '/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

AUTHORS_DB_REST_ENDPOINT = {
    'pid_type': 'aut',
    'search_class': 'inspirehep.modules.search:AuthorsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/authors/db',
    'item_route': '/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

AUTHORS_CITATION_REST_ENDPOINT = {
    'pid_type': 'aut',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:AuthorsSearch',
    'record_serializers': {
        'application/json': 'inspirehep.modules.authors.rest:citations_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/authors/citations',
    'item_route': '/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/citations',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

AUTHORS_COAUTHORS_REST_ENDPOINT = {
    'pid_type': 'aut',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:AuthorsSearch',
    'record_serializers': {
        'application/json': 'inspirehep.modules.authors.rest:coauthors_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/authors/coauthors',
    'item_route': '/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/coauthors',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

AUTHORS_PUBLICATIONS_REST_ENDPOINT = {
    'pid_type': 'aut',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:AuthorsSearch',
    'record_serializers': {
        'application/json': 'inspirehep.modules.authors.rest:publications_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/authors/publications',
    'item_route': '/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/publications',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

AUTHORS_STATS_REST_ENDPOINT = {
    'pid_type': 'aut',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:AuthorsSearch',
    'record_serializers': {
        'application/json': 'inspirehep.modules.authors.rest:stats_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/authors/stats',
    'item_route': '/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/stats',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

DATA_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'dat',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:DataSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/data/',
    'item_route': '/data/<pid(dat,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

DATA_DB_REST_ENDPOINT = {
    'pid_type': 'dat',
    'search_class': 'inspirehep.modules.search:DataSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/data/db',
    'item_route': '/data/<pid(dat,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

CONFERENCES_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'con',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:ConferencesSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
        'application/vnd+inspire.ids+json': 'inspirehep.modules.api.v1.common_serializers:json_recids_response',
    },
    'suggesters': {
        'conference': {
            '_source': [
                'acronyms',
                'titles',
                'addresses',
                'opening_date'
                'cnum'
                'control_number',
                'self',
            ],
            'completion': {
                'field': 'conferenceautocomplete'
            }
        }
    },
    'list_route': '/conferences/',
    'item_route': '/conferences/<pid(con,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

CONFERENCES_DB_REST_ENDPOINT = {
    'pid_type': 'con',
    'search_class': 'inspirehep.modules.search:ConferencesSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/conferences/db',
    'item_route': '/conferences/<pid(con,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

JOBS_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'job',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:JobsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
        'application/vnd+inspire.ids+json': 'inspirehep.modules.api.v1.common_serializers:json_recids_response',
    },
    'list_route': '/jobs/',
    'item_route': '/jobs/<pid(job,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

JOBS_DB_REST_ENDPOINT = {
    'pid_type': 'job',
    'search_class': 'inspirehep.modules.search:JobsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/jobs/db',
    'item_route': '/jobs/<pid(job,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

INSTITUTIONS_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'ins',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:InstitutionsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
        'application/vnd+inspire.ids+json': 'inspirehep.modules.api.v1.common_serializers:json_recids_response',
    },
    'suggesters': {
        'affiliation': {
            '_source': [
                'legacy_ICN',
                'control_number',
                'self',
            ],
            'completion': {
                'field': 'affiliation_suggest',
            },
        },
    },
    'list_route': '/institutions/',
    'item_route': '/institutions/<pid(ins,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

INSTITUTIONS_DB_REST_ENDPOINT = {
    'pid_type': 'ins',
    'search_class': 'inspirehep.modules.search:InstitutionsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/institutions/db',
    'item_route': '/institutions/<pid(ins,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

EXPERIMENTS_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'exp',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:ExperimentsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
        'application/vnd+inspire.ids+json': 'inspirehep.modules.api.v1.common_serializers:json_recids_response',
    },
    'suggesters': {
        'experiment': {
            '_source': [
                'legacy_name',
                'control_number',
                'self',
            ],
            'completion': {
                'field': 'experiment_suggest',
            },
        },
    },
    'list_route': '/experiments/',
    'item_route': '/experiments/<pid(exp,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

EXPERIMENTS_DB_REST_ENDPOINT = {
    'pid_type': 'exp',
    'search_class': 'inspirehep.modules.search:ExperimentsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/experiments/db',
    'item_route': '/experiments/<pid(exp,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

JOURNALS_REST_ENDPOINT = {
    'default_endpoint_prefix': True,
    'pid_type': 'jou',
    'pid_minter': 'inspire_recid_minter',
    'pid_fetcher': 'inspire_recid_fetcher',
    'search_class': 'inspirehep.modules.search:JournalsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
        'application/vnd+inspire.ids+json': 'inspirehep.modules.api.v1.common_serializers:json_recids_response',
    },
    'suggesters': {
        'journal_title': {
            '_source': [
                'short_title',
                'journal_title',
                'control_number',
                'self',
            ],
            'completion': {
                'field': 'title_suggest',
                'size': 10,
            },
        },
    },
    'list_route': '/journals/',
    'item_route': '/journals/<pid(jou,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
}

JOURNALS_DB_REST_ENDPOINT = {
    'pid_type': 'jou',
    'search_class': 'inspirehep.modules.search:JournalsSearch',
    'record_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_response',
    },
    'record_class': 'inspirehep.modules.records.api:InspireRecord',
    'search_serializers': {
        'application/json': 'invenio_records_rest.serializers:json_v1_search',
    },
    'list_route': '/journals/db',
    'item_route': '/journals/<pid(jou,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
    'default_media_type': 'application/json',
    'search_factory_imp': 'inspirehep.modules.search.search_factory:inspire_search_factory',
    'update_permission_factory_imp': "inspirehep.modules.records.permissions:record_update_permission_factory",
}

RECORDS_REST_ENDPOINTS = {
    'literature': LITERATURE_REST_ENDPOINT,
    'literature_references': LITERATURE_REFERENCES_REST_ENDPOINT,
    'literature_authors': LITERATURE_AUTHORS_REST_ENDPOINT,
    'authors': AUTHORS_REST_ENDPOINT,
    'authors_db': AUTHORS_DB_REST_ENDPOINT,
    'authors_citations': AUTHORS_CITATION_REST_ENDPOINT,
    'authors_coauthors': AUTHORS_COAUTHORS_REST_ENDPOINT,
    'authors_publications': AUTHORS_PUBLICATIONS_REST_ENDPOINT,
    'authors_stats': AUTHORS_STATS_REST_ENDPOINT,
    'data': DATA_REST_ENDPOINT,
    'data_db': DATA_DB_REST_ENDPOINT,
    'conferences': CONFERENCES_REST_ENDPOINT,
    'conferences_db': CONFERENCES_DB_REST_ENDPOINT,
    'jobs': JOBS_REST_ENDPOINT,
    'jobs_db': JOBS_DB_REST_ENDPOINT,
    'institutions': INSTITUTIONS_REST_ENDPOINT,
    'institutions_db': INSTITUTIONS_DB_REST_ENDPOINT,
    'experiments': EXPERIMENTS_REST_ENDPOINT,
    'experiments_db': EXPERIMENTS_DB_REST_ENDPOINT,
    'journals': JOURNALS_REST_ENDPOINT,
    'journals_db': JOURNALS_DB_REST_ENDPOINT,
}

RECORDS_UI_DEFAULT_PERMISSION_FACTORY = "inspirehep.modules.records.permissions:record_read_permission_factory"

RECORDS_UI_ENDPOINTS = {
    'literature': {
        'pid_type': 'lit',
        'route': '/old-literature/<pid_value>',
        'template': 'inspirehep_theme/format/record/Inspire_Default_HTML_detailed.tpl',
        'record_class': 'inspirehep.modules.records.wrappers:LiteratureRecord',
    },
    'authors': {
        'pid_type': 'aut',
        'route': '/authors/<pid_value>',
        'template': 'inspirehep_theme/format/record/authors/Author_HTML_detailed.html',
        'record_class': 'inspirehep.modules.records.wrappers:AuthorsRecord',
    },
    'data': {
        'pid_type': 'dat',
        'route': '/data/<pid_value>',
        'template': 'inspirehep_theme/format/record/Data_HTML_detailed.tpl'
    },
    'conferences': {
        'pid_type': 'con',
        'route': '/conferences/<pid_value>',
        'template': 'inspirehep_theme/format/record/Conference_HTML_detailed.tpl',
        'record_class': 'inspirehep.modules.records.wrappers:ConferencesRecord',
    },
    'jobs': {
        'pid_type': 'job',
        'route': '/jobs/<pid_value>',
        'template': 'inspirehep_theme/format/record/Job_HTML_detailed.tpl',
        'record_class': 'inspirehep.modules.records.wrappers:JobsRecord',
    },
    'institutions': {
        'pid_type': 'ins',
        'route': '/institutions/<pid_value>',
        'template': 'inspirehep_theme/format/record/Institution_HTML_detailed.tpl',
        'record_class': 'inspirehep.modules.records.wrappers:InstitutionsRecord',
    },
    'experiments': {
        'pid_type': 'exp',
        'route': '/experiments/<pid_value>',
        'template': 'inspirehep_theme/format/record/Experiment_HTML_detailed.tpl',
        'record_class': 'inspirehep.modules.records.wrappers:ExperimentsRecord',
    },
    'journals': {
        'pid_type': 'jou',
        'route': '/journals/<pid_value>',
        'template': 'inspirehep_theme/format/record/Journal_HTML_detailed.tpl',
        'record_class': 'inspirehep.modules.records.wrappers:JournalsRecord',
    },
}

RECORDS_REST_FACETS = {
    "hep-author-publication": hep_author_publications,
    "records-hep": {
        "filters": {
            "author": must_match_all_filter('facet_author_name'),
            "author_count": range_author_count_filter('author_count'),
            "subject": must_match_all_filter('facet_inspire_categories'),
            "arxiv_categories": must_match_all_filter('facet_arxiv_categories'),
            "doc_type": must_match_all_filter('facet_inspire_doc_type'),
            "experiment": must_match_all_filter('facet_experiment'),
            "earliest_date": range_filter(
                'earliest_date',
                format='yyyy',
                end_date_math='/y')
        },
        "aggs": {
            "earliest_date": {
                "date_histogram": {
                    "field": "earliest_date",
                    "interval": "year",
                    "format": "yyyy",
                    "min_doc_count": 1,
                },
                "meta": {
                    "title": "Date",
                    "order": 1,
                },
            },
            "author_count": {
                "range": {
                    "field": "author_count",
                    "ranges": [
                        {
                            "key": "10 authors or less",
                            "from": 1,
                            "to": 11,
                        },
                    ],
                },
                "meta": {
                    "title": "Number of authors",
                    "order": 2,
                },
            },
            "author": {
                "terms": {
                    "field": "facet_author_name",
                    "size": 20
                },
                "meta": {
                    "title": "Author",
                    "order": 3,
                    "split": True,
                },
            },
            "subject": {
                "terms": {
                    "field": "facet_inspire_categories",
                    "size": 20
                },
                "meta": {
                    "title": "Subject",
                    "order": 4,
                }
            },
            "arxiv_categories": {
                "terms": {
                    "field": "facet_arxiv_categories",
                    "size": 20
                },
                "meta": {
                    "title": "arXiv Category",
                    "order": 5,
                },
            },
            "experiment": {
                "terms": {
                    "field": "facet_experiment",
                    "size": 20
                },
                "meta": {
                    "title": "Experiment",
                    "order": 6,
                },
            },
            "doc_type": {
                "terms": {
                    "field": "facet_inspire_doc_type",
                    "size": 20
                },
                "meta": {
                    "title": "Document Type",
                    "order": 7,
                },
            },
        }
    },
    "records-authors": {
        "filters": {
            "arxiv_categories": terms_filter('facet_arxiv_categories'),
            "institution": terms_filter('facet_institution_name')
        },
        "aggs": {
            "arxiv_categories": {
                "terms": {
                    "field": "facet_arxiv_categories",
                    "size": 20
                }
            },
            "institution": {
                "terms": {
                    "field": "facet_institution_name",
                    "size": 20
                }
            }
        }
    },
    "records-conferences": {
        "filters": {
            "series": terms_filter('series'),
            "inspire_categories": terms_filter('inspire_categories.term'),
        },
        "aggs": {
            "series": {
                "terms": {
                    "field": "series",
                    "size": 20
                }
            },
            "inspire_categories": {
                "terms": {
                    "field": "inspire_categories.term",
                    "size": 20
                }
            },
            "opening_date": {
                "date_histogram": {
                    "field": "opening_date",
                    "interval": "year",
                    "format": "yyyy",
                    "min_doc_count": 1,
                }
            }
        }
    },
    "records-experiments": {
        "filters": {
            "field_code": terms_filter('field_code'),
            "affiliation": terms_filter('affiliation'),
            "collaboration": terms_filter('collaboration')
        },
        "aggs": {
            "field_code": {
                "terms": {
                    "field": "field_code",
                    "size": 20
                }
            },
            "affiliation": {
                "terms": {
                    "field": "affiliation",
                    "size": 20
                }
            },
            "collaboration": {
                "terms": {
                    "field": "collaboration",
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
            "regions": terms_filter('regions'),
            "ranks": terms_filter('ranks'),
            "inspire_categories": terms_filter('inspire_categories.term')
        },
        "aggs": {
            "continent": {
                "terms": {
                    "field": "regions",
                    "size": 20
                }
            },
            "ranks": {
                "terms": {
                    "field": "ranks",
                    "size": 20
                }
            },
            "inspire_categories": {
                "terms": {
                    "field": "inspire_categories.term",
                    "size": 20
                }
            }
        }
    }
}

RECORDS_REST_SORT_OPTIONS = {
    "records-hep": {
        "mostrecent": {
            "title": 'Most recent',
            "fields": ['-earliest_date'],
            "default_order": 'asc',  # Used for invenio-search-js config
            "order": 1,
        },
        "mostcited": {
            "title": 'Most cited',
            "fields": ['-citation_count'],
            "default_order": 'asc',  # Used for invenio-search-js config
            "order": 2,
        },
        "bestmatch": {
            "title": 'Best Match',
            "fields": ['-_score'],
            "default_order": 'asc',
            "order": 3,
        },
    },

    "record-data": {
        'latest': {'fields': 'latest', 'default_order': 'asc',
                   'order': 1, 'title': 'Recent'},

        'relevance': {'fields': 'relevance', 'default_order': 'asc',
                      'order': 2, 'title': 'Relevance'},

        'title': {'fields': 'title', 'default_order': 'asc',
                  'order': 3, 'title': 'Title'},

        'collaborations': {'fields': 'collaborations', 'default_order': 'asc',
                           'order': 4, 'title': 'Collaboration'},

        'date': {'fields': 'date', 'default_order': 'asc',
                 'order': 5, 'title': 'Publication Date'}
    },

    "records-jobs": {
        "bestmatch": {
            "title": 'Best match',
            "fields": ['_score'],
            "default_order": 'desc',
            "order": 1,
        },
        "mostrecent": {
            "title": 'Most recent',
            "fields": ['earliest_date'],
            "default_order": 'desc',
            "order": 2,
        },
    }
}

RECORDS_REST_DEFAULT_SORT = {
    "records-hep": {
        "query": "mostrecent",
        "noquery": "mostrecent"
    },

    "records-data": {
        "query": "relevance",
        "noquery": "latest"
    },

    "records-jobs": {
        "query": "bestmatch",
        "noquery": "mostrecent"
    }
}

RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY = None

RECORDS_VALIDATION_TYPES = {
    'array': (list, tuple),
}

RECORDS_SKIP_FILES = False
"""Disable the downloading of files at record creation and update times.

Note:

  The ``skip_files`` parameter passed to ``InspireRecord.create`` or
  ``InspireRecord.update`` takes precedence on this config variable.

"""
RECORDS_MIGRATION_SKIP_FILES = False
"""Disable the downloading of files at record migration time.

Note:

  This variable takes precedence over ``RECORDS_SKIP_FILES``, but can be
  overriden by the tasks in the ``inspirehep.modules.migrator.tasks`` module.
"""

JSONSCHEMAS_HOST = "localhost:5000"
JSONSCHEMAS_REPLACE_REFS = True
JSONSCHEMAS_LOADER_CLS = 'inspirehep.modules.records.json_ref_loader.SCHEMA_LOADER_CLS'

INDEXER_DEFAULT_INDEX = "records-hep"
INDEXER_DEFAULT_DOC_TYPE = "_doc"
INDEXER_REPLACE_REFS = False
INDEXER_BULK_REQUEST_TIMEOUT = float(900)

# OAuthclient
# ===========
orcid.REMOTE_MEMBER_APP['params']['request_token_params'] = {
    'scope': ' '.join([
        '/read-limited',
        '/activities/update',
        '/person/update',
    ]),
    'show_login': 'true',
}

orcid.REMOTE_MEMBER_APP['signup_handler']['setup'] = 'inspirehep.modules.orcid.utils.account_setup'

orcid.REMOTE_MEMBER_APP['remember'] = True
OAUTHCLIENT_REMOTE_APPS = {
    'orcid': orcid.REMOTE_MEMBER_APP,
}
OAUTHCLIENT_ORCID_CREDENTIALS = {
    'consumer_key': 'CHANGE_ME',
    'consumer_secret': 'CHANGE_ME',
}
ORCID_ALLOW_PUSH_DEFAULT = False

OAUTHCLIENT_SETTINGS_TEMPLATE = 'inspirehep_theme/page.html'

# Inspire service client for ORCID.
ORCID_APP_CREDENTIALS = {
    'consumer_key': 'CHANGE_ME',
    'consumer_secret': 'CHANGE_ME',
}

# Error Pages
# ========
THEME_401_TEMPLATE = "inspirehep_theme/errors/401.html"
THEME_403_TEMPLATE = "inspirehep_theme/errors/403.html"
THEME_404_TEMPLATE = "inspirehep_theme/errors/404.html"
THEME_500_TEMPLATE = "inspirehep_theme/errors/500.html"

# Feedback
# ========
CFG_SITE_SUPPORT_EMAIL = "admin@inspirehep.net"
INSPIRELABS_FEEDBACK_EMAIL = "labsfeedback@inspirehep.net"

# Submission
# ==========
LEGACY_ROBOTUPLOAD_URL = None  # Disabled by default
LEGACY_MATCH_ENDPOINT = "http://inspirehep.net/search"
LEGACY_ROBOTUPLOAD_PRIORITY_ARTICLE = 4
LEGACY_ROBOTUPLOAD_PRIORITY_AUTHOR = 4
LEGACY_ROBOTUPLOAD_PRIORITY_EDIT_ARTICLE = 5

# Web services and APIs
# =====================
CLASSIFIER_API_URL = None  # e.g. "http://inspire-classifier.web.cern.ch/api"
MAGPIE_API_URL = None  # e.g. "http://magpie.inspirehep.net/api"
LEGACY_BASE_URL = "https://old.inspirehep.net"
LEGACY_RECORD_URL_PATTERN = 'http://inspirehep.net/record/{recid}'
AUTHENTICATION_TOKEN = "CHANGE_ME"
INSPIREHEP_URL = "http://web:8000"
FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT = False

# Harvesting and Workflows
# ========================
AFFILIATIONS_TO_HIDDEN_COLLECTIONS_MAPPING = {
    "IN2P3": "HAL Hidden",
    "CPPM": "HAL Hidden",
    "GANIL": "HAL Hidden",
    "IJCLAB": "HAL Hidden",
    "IP2I": "HAL Hidden",
    "IPHC": "HAL Hidden",
    "L2IT": "HAL Hidden",
    "LNCA": "HAL Hidden",
    "LP2I": "HAL Hidden",
    "LPNHE": "HAL Hidden",
    "LPSC": "HAL Hidden",
    "LUPM": "HAL Hidden",
    "SUBATECH": "HAL Hidden",
    "BINETRUY": "HAL Hidden",
    u"BINÉTRUY": "HAL Hidden",
    "ILANCE": "HAL Hidden",
    "DMLAB": "HAL Hidden",
    "RINGUET": "HAL Hidden",
    "YUASA": "HAL Hidden",
    "AICP": "HAL Hidden",
    "MODANE": "HAL Hidden",
    "LPCA": "HAL Hidden",
    "INFINIS": "HAL Hidden",
    "IRENE JOLIOT": "HAL Hidden",
    u"IRÈNE JOLIOT": "HAL Hidden",
    "IONS LOURDS": "HAL Hidden",
    "ASTROPARTICULE ET COSMOLOGIE": "HAL Hidden",
    "UNIVERS ET PARTICULES": "HAL Hidden",
    "PLURIDISCIPLINAIRE HUBERT CURIEN": "HAL Hidden",
    "CERN": "CDS Hidden",
    "FERMILAB": "Fermilab"
}
ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}"
ARXIV_PDF_URL_ALTERNATIVE = "https://export.arxiv.org/pdf/{arxiv_id}"
ARXIV_TARBALL_URL = "https://arxiv.org/e-print/{arxiv_id}"

ARXIV_CATEGORIES = {
    'core': [
        'hep-ex',
        'hep-lat',
        'hep-ph',
        'hep-th'
    ],
    'non-core': [
        'astro-ph.CO',
        'astro-ph.HE',
        'gr-qc',
        'nucl-ex',
        'nucl-th',
        'physics.acc-ph',
        'physics.ins-det',
        'quant-ph'
    ]
}
JLAB_ARXIV_CATEGORIES = [
    'nucl-th'
]
HEP_ONTOLOGY_FILE = "HEPont.rdf"
"""Name or path of the ontology to use for hep articles keyword extraction."""

RECORDS_DEFAULT_FILE_LOCATION_NAME = "records"
"""Name of default records Location reference."""

RECORDS_DEFAULT_STORAGE_CLASS = "S"
"""Default storage class for record files."""

WORKFLOWS_DEFAULT_FILE_LOCATION_NAME = "holdingpen"
"""Name of default workflow Location reference."""

WORKFLOWS_OBJECT_CLASS = "invenio_workflows_files.api.WorkflowObject"
"""Enable obj.files API."""

WORKFLOWS_RESTART_LIMIT = 3
"""Max number of times a workflow can be restarted."""

WORKFLOWS_UI_BASE_TEMPLATE = BASE_TEMPLATE
WORKFLOWS_UI_INDEX_TEMPLATE = "inspire_workflows/index.html"
WORKFLOWS_UI_LIST_TEMPLATE = "inspire_workflows/list.html"
WORKFLOWS_UI_DETAILS_TEMPLATE = "inspire_workflows/details.html"
WORKFLOWS_UI_LIST_ROW_TEMPLATE = "inspire_workflows/list_row.html"

WORKFLOWS_UI_URL = "/holdingpen"
WORKFLOWS_UI_API_URL = "/api/holdingpen/"
WORKFLOWS_EDITOR_API_URL = "/editor/holdingpen/"

WORKFLOWS_UI_REST_ENDPOINT = {
    'workflow_object_serializers': {
        'application/json': 'invenio_workflows_ui.serializers:json_serializer',
    },
    'search_serializers': {
        'application/json': 'invenio_workflows_ui.serializers:json_search_serializer',
    },
    'action_serializers': {
        'application/json': 'invenio_workflows_ui.serializers:json_action_serializer',
    },
    'bulk_action_serializers': {
        'application/json': 'invenio_workflows_ui.serializers:json_action_serializer',
    },
    'file_serializers': {
        'application/json': 'invenio_workflows_ui.serializers:json_file_serializer',
    },
    'list_route': '/holdingpen/',
    'item_route': '/holdingpen/<object_id>',
    'file_list_route': '/holdingpen/<object_id>/files',
    'file_item_route': '/holdingpen/<object_id>/files/<path:key>',
    'search_index': 'holdingpen',
    'search_factory_imp': 'inspirehep.modules.workflows.search:holdingpen_search_factory',
    'default_media_type': 'application/json',
    'max_result_window': 10000,
}

WORKFLOWS_UI_DATA_TYPES = {
    'hep': {
        'search_index': 'holdingpen-hep',
        'search_type': '_doc',
    },
    'authors': {
        'search_index': 'holdingpen-authors',
        'search_type': '_doc',
    }
}

WORKFLOWS_UI_REST_FACETS = {
    "holdingpen": {
        "filters": {
            "pending_action": terms_filter('_extra_data._action'),
            "status": terms_filter('_workflow.status'),
            "source": terms_filter('metadata.acquisition_source.source'),
            "method": terms_filter('metadata.acquisition_source.method'),
            "workflow_name": terms_filter('_workflow.workflow_name'),
            "is-update": terms_filter('_extra_data.is-update'),
            'subject': terms_filter('metadata.inspire_categories.term'),
            'decision': terms_filter('_extra_data.relevance_prediction.decision'),
            'journal': terms_filter('metadata.facet_journal_title'),
        },
        "aggs": {
            "status": {
                "terms": {
                    "field": "_workflow.status",
                    "size": 20
                }
            },
            "source": {
                "terms": {
                    "field": "metadata.acquisition_source.source",
                    "size": 20
                }
            },
            "workflow_name": {
                "terms": {
                    "field": "_workflow.workflow_name",
                    "size": 20
                }
            },
            'subject': {
                'terms': {
                    'field': 'metadata.inspire_categories.term',
                    'size': 20,
                },
            },
            'decision': {
                'terms': {
                    'field': '_extra_data.relevance_prediction.decision',
                    'size': 20,
                },
            },
            'pending_action': {
                'terms': {
                    'field': '_extra_data._action',
                },
            },
            'journal': {
                'terms': {
                    'field': 'metadata.facet_journal_title',
                    'size': 20
                },
            },
        }
    }
}

WORKFLOWS_UI_REST_SORT_OPTIONS = {
    "holdingpen": {
        "bestmatch": {
            "title": 'Best match',
            "fields": ['-_score'],
            "default_order": 'asc',
            "order": 1,
        },
        "mostrecent": {
            "title": 'Most recent',
            "fields": ['-metadata.acquisition_source.datetime'],
            "default_order": 'asc',
            "order": 2,
        },
        'core': {
            'title': 'Relevance Prediction (Desc)',
            'fields': [
                {
                    '_extra_data.relevance_prediction.relevance_score': {
                        'missing': '_last',
                        'order': 'desc',
                        'unmapped_type': 'float',
                    },
                },
            ],
            'order': 3,
        },
        'rejected': {
            'title': 'Relevance Prediction (Asc)',
            'fields': [
                {
                    '_extra_data.relevance_prediction.relevance_score': {
                        'missing': '_last',
                        'order': 'asc',
                        'unmapped_type': 'float',
                    },
                },
            ],
            'order': 4,
        },
    },
}

WORKFLOWS_UI_REST_DEFAULT_SORT = {
    "holdingpen": {
        "query": "mostrecent",
        "noquery": "mostrecent"
    }
}

# Crawling
# ========

CRAWLER_HOST_URL = "http://localhost:6800"

CRAWLER_SETTINGS = {
    # URL to your flower instance
    "API_PIPELINE_URL": "http://localhost:5555/api/task/async-apply",
    "API_PIPELINE_TASK_ENDPOINT_DEFAULT": "inspire_crawler.tasks.submit_results",
}
# Legacy PID provider
# ===================
LEGACY_PID_PROVIDER = None  # e.g. "http://example.org/batchuploader/allocaterecord"

# Inspire subject translation
# ===========================
ARXIV_TO_INSPIRE_CATEGORY_MAPPING = {
    "alg-geom": "Math and Math Physics",
    "astro-ph": "Astrophysics",
    "astro-ph.CO": "Astrophysics",
    "astro-ph.EP": "Astrophysics",
    "astro-ph.GA": "Astrophysics",
    "astro-ph.HE": "Astrophysics",
    "astro-ph.IM": "Instrumentation",
    "astro-ph.SR": "Astrophysics",
    "cond-mat": "General Physics",
    "cond-mat.dis-nn": "General Physics",
    "cond-mat.mes-hall": "General Physics",
    "cond-mat.mtrl-sci": "General Physics",
    "cond-mat.other": "General Physics",
    "cond-mat.quant-gas": "General Physics",
    "cond-mat.soft": "General Physics",
    "cond-mat.stat-mech": "General Physics",
    "cond-mat.str-el": "General Physics",
    "cond-mat.supr-con": "General Physics",
    "cs": "Computing",
    "cs.AI": "Computing",
    "cs.AR": "Computing",
    "cs.CC": "Computing",
    "cs.CE": "Computing",
    "cs.CG": "Computing",
    "cs.CL": "Computing",
    "cs.CR": "Computing",
    "cs.CV": "Computing",
    "cs.CY": "Computing",
    "cs.DB": "Computing",
    "cs.DC": "Computing",
    "cs.DL": "Computing",
    "cs.DM": "Computing",
    "cs.DS": "Computing",
    "cs.ET": "Computing",
    "cs.FL": "Computing",
    "cs.GL": "Computing",
    "cs.GR": "Computing",
    "cs.GT": "Computing",
    "cs.HC": "Computing",
    "cs.IR": "Computing",
    "cs.IT": "Computing",
    "cs.LG": "Computing",
    "cs.LO": "Computing",
    "cs.MA": "Computing",
    "cs.MM": "Computing",
    "cs.MS": "Computing",
    "cs.NA": "Computing",
    "cs.NE": "Computing",
    "cs.NI": "Computing",
    "cs.OH": "Computing",
    "cs.OS": "Computing",
    "cs.PF": "Computing",
    "cs.PL": "Computing",
    "cs.RO": "Computing",
    "cs.SC": "Computing",
    "cs.SD": "Computing",
    "cs.SE": "Computing",
    "cs.SI": "Computing",
    "cs.SY": "Computing",
    "dg-ga": "Math and Math Physics",
    "gr-qc": "Gravitation and Cosmology",
    "hep-ex": "Experiment-HEP",
    "hep-lat": "Lattice",
    "hep-ph": "Phenomenology-HEP",
    "hep-th": "Theory-HEP",
    "math": "Math and Math Physics",
    "math-ph": "Math and Math Physics",
    "math.AC": "Math and Math Physics",
    "math.AG": "Math and Math Physics",
    "math.AP": "Math and Math Physics",
    "math.AT": "Math and Math Physics",
    "math.CA": "Math and Math Physics",
    "math.CO": "Math and Math Physics",
    "math.CT": "Math and Math Physics",
    "math.CV": "Math and Math Physics",
    "math.DG": "Math and Math Physics",
    "math.DS": "Math and Math Physics",
    "math.FA": "Math and Math Physics",
    "math.GM": "Math and Math Physics",
    "math.GN": "Math and Math Physics",
    "math.GR": "Math and Math Physics",
    "math.GT": "Math and Math Physics",
    "math.HO": "Math and Math Physics",
    "math.IT": "Math and Math Physics",
    "math.KT": "Math and Math Physics",
    "math.LO": "Math and Math Physics",
    "math.MG": "Math and Math Physics",
    "math.MP": "Math and Math Physics",
    "math.NA": "Math and Math Physics",
    "math.NT": "Math and Math Physics",
    "math.OA": "Math and Math Physics",
    "math.OC": "Math and Math Physics",
    "math.PR": "Math and Math Physics",
    "math.QA": "Math and Math Physics",
    "math.RA": "Math and Math Physics",
    "math.RT": "Math and Math Physics",
    "math.SG": "Math and Math Physics",
    "math.SP": "Math and Math Physics",
    "math.ST": "Math and Math Physics",
    "nlin": "General Physics",
    "nlin.AO": "General Physics",
    "nlin.CD": "General Physics",
    "nlin.CG": "General Physics",
    "nlin.PS": "Math and Math Physics",
    "nlin.SI": "Math and Math Physics",
    "nucl-ex": "Experiment-Nucl",
    "nucl-th": "Theory-Nucl",
    "patt-sol": "Math and Math Physics",
    "physics": "General Physics",
    "physics.acc-ph": "Accelerators",
    "physics.ao-ph": "General Physics",
    "physics.atm-clus": "General Physics",
    "physics.atom-ph": "General Physics",
    "physics.bio-ph": "Other",
    "physics.chem-ph": "Other",
    "physics.class-ph": "General Physics",
    "physics.comp-ph": "Computing",
    "physics.data-an": "Data Analysis and Statistics",
    "physics.ed-ph": "Other",
    "physics.flu-dyn": "General Physics",
    "physics.gen-ph": "General Physics",
    "physics.geo-ph": "General Physics",
    "physics.hist-ph": "Other",
    "physics.ins-det": "Instrumentation",
    "physics.med-ph": "Other",
    "physics.optics": "General Physics",
    "physics.plasm-ph": "General Physics",
    "physics.pop-ph": "Other",
    "physics.soc-ph": "Other",
    "physics.space-ph": "Astrophysics",
    "q-alg": "Math and Math Physics",
    "q-bio": "Other",
    "q-bio.BM": "Other",
    "q-bio.CB": "Other",
    "q-bio.GN": "Other",
    "q-bio.MN": "Other",
    "q-bio.NC": "Other",
    "q-bio.OT": "Other",
    "q-bio.PE": "Other",
    "q-bio.QM": "Other",
    "q-bio.SC": "Other",
    "q-bio.TO": "Other",
    "q-fin": "Other",
    "q-fin.CP": "Other",
    "q-fin.EC": "Other",
    "q-fin.GN": "Other",
    "q-fin.MF": "Other",
    "q-fin.PM": "Other",
    "q-fin.PR": "Other",
    "q-fin.RM": "Other",
    "q-fin.ST": "Other",
    "q-fin.TR": "Other",
    "quant-ph": "General Physics",
    "solv-int": "Math and Math Physics",
    "stat": "Other",
    "stat.AP": "Other",
    "stat.CO": "Other",
    "stat.ME": "Other",
    "stat.ML": "Other",
    "stat.OT": "Other",
    "stat.TH": "Other"
}

# Configuration for the $ref updater
# ==================================
INSPIRE_REF_UPDATER_WHITELISTS = {
    'authors': [
        'advisors.record',
        'conferences',
        'experiments.record',
        'posititions.institutions.record',
    ],
    'conferences': [],
    'experiments': [
        'affiliation.record',
        'related_records.record',
        'spokespersons.record',
    ],
    'literature': [
        'accelerator_experiments.record',
        'authors.affiliations.record',
        'authors.record',
        'collaboration.record',
        'publication_info.conference_record',
        'publication_info.journal_record',
        'publication_info.parent_record',
        'references.record',
        'related_records.record',
        'thesis.institutions.record',
        'thesis_supervisors.affiliations.record',
    ],
    'institutions': [
        'related_records.record',
    ],
    'jobs': [
        'experiments.record',
        'institutions.record',
    ],
    'journals': [
        'related_records.record',
    ],
}
"""Controls which fields are updated when the referred record is updated."""

# App metrics
# ===========
APPMETRICS_ELASTICSEARCH_HOSTS = ['localhost']
APPMETRICS_ELASTICSEARCH_INDEX = 'inspireappmetrics-dev'
APPMETRICS_THREADED_BACKEND = True

BATCHUPLOADER_WEB_ROBOT_TOKEN = 'change me'

# refextract
# ==========
FEATURE_FLAG_ENABLE_REFEXTRACT_SERVICE = False
REFEXTRACT_SERVICE_URL = 'http://example_refextract_url.cern.ch'

# logging
# ==========
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s: %(levelname)s/%(processName)s] %(name)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "inspirehep.modules": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": True
            },
            "inspire_utils.record": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": True
            },
            "": {
                "level": "INFO",
                "handlers": ["console"]
            }
        },
    }
)

# SNOW
QUEUE_TO_FUNCTIONAL_CATEGORY_MAPPING = {
    "HEP_add_user": "Literature submissions",
    "HAL_curation": "HAL curation",
    "UK_curation": "UK curation",
    "CERN_curation": "CDS curation",
    "GER_curation": "German curation",
    "HEP_curation": "arXiv curation",
    "HEP_curation_jlab": "arXiv curation",
    "HEP_publishing": "Publisher curation",
    "AUTHORS_curation": "Author curation",
    "Authors_cor_user": "Author updates",
    "Authors_add_user": "Author submissions"
}
