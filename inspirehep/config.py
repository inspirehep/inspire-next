# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""INSPIREHEP app configuration."""

from __future__ import absolute_import, division, print_function

import os
import sys

from invenio_oauthclient.contrib import orcid
from invenio_records_rest.facets import range_filter, terms_filter

from inspirehep.modules.records.utils import get_detailed_template_from_record


def _(x):
    """Identity function for string extraction."""
    return x


# Debug
# =====
DEBUG_TB_INTERCEPT_REDIRECTS = False
SERVER_NAME = 'localhost:5000'

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
THEME_SITENAME = _("inspirehep")
BASE_TEMPLATE = "inspirehep_theme/page.html"

# Database
# ========
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://inspirehep:dbpass123@localhost:5432/inspirehep"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Celery
# ======
BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND = "amqp://guest:guest@localhost:5672//"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TIMEZONE = 'Europe/Amsterdam'
CELERY_DISABLE_RATE_LIMITS = True

# Cache
# =====
CACHE_KEY_PREFIX = "cache::"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_TYPE = "redis"
ACCOUNTS_SESSION_REDIS_URL = "redis://localhost:6379/2"

# Files
# =====
BASE_FILES_LOCATION = os.path.join(sys.prefix, 'var/data')

# REST
# ====
REST_ENABLE_CORS = True

# Logging
# =======
# To enable file logging set it to e.g. "{sys_prefix}/var/log/inspirehep.log"
LOGGING_FS_LOGFILE = None

# Overwrite default Sentry extension class to support Sentry 6.
LOGGING_SENTRY_CLASS = 'invenio_logging.sentry6:Sentry6'

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

COLLECTIONS_QUERY_PARSER = 'inspirehep.modules.search.parser:Main'
"""User search query lexical parser."""

COLLECTIONS_QUERY_WALKERS = [
    'inspirehep.modules.search.walkers.pypeg_to_ast:PypegConverter',
]
"""Modules to create the query AST."""

COLLECTIONS_USE_PERCOLATOR = False
"""Define which percolator you want to use.

Default value is `False` to use the internal percolator.
You can also set True to use ElasticSearch to provide percolator resolver.
NOTE that ES percolator uses high memory and there might be some problems
when creating records.
"""

RECORD_EDITOR_INDEX_TEMPLATE = 'inspirehep_theme/invenio_record_editor/index.html'
RECORD_EDITOR_PREVIEW_TEMPLATE_FUNCTION = get_detailed_template_from_record

INSPIRE_COLLECTIONS_DEFINITION = [
    {
        'query': '_collections:Literature',
        'name': 'Literature',
    },
    {
        'query': '_collections:Authors',
        'name': 'Authors',
    },
    {
        'query': '_collections:Data',
        'name': 'Data',
    },
    {
        'query': '_collections:Conferences',
        'name': 'Conferences',
    },
    {
        'query': '_collections:Jobs',
        'name': 'Jobs',
    },
    {
        'query': '_collections:Institutions',
        'name': 'Institutions',
    },
    {
        'query': '_collections:Experiments',
        'name': 'Experiments',
    },
    {
        'query': '_collections:Journals',
        'name': 'Journals',
    },
    {
        'query': 'special_collections:CDF-INTERNAL-NOTE',
        'name': 'CDF Internal Notes',
    },
    {
        'query': 'special_collections:CDF-NOTE',
        'name': 'CDF Notes',
    },
    {
        'query': 'special_collections:D0-INTERNAL-NOTE',
        'name': 'D0 Internal Notes',
    },
    {
        'query': 'special_collections:D0-PRELIMINARY-NOTE',
        'name': 'D0 Preliminary Notes',
    },
    {
        'query': 'special_collections:H1-INTERNAL-NOTE',
        'name': 'H1 Internal Notes',
    },
    {
        'query': 'special_collections:H1-PRELIMINARY-NOTE',
        'name': 'H1 Preliminary Notes',
    },
    {
        'query': 'special_collections:HALHIDDEN',
        'name': 'HAL Hidden',
    },
    {
        'query': 'special_collections:HEPHIDDEN',
        'name': 'HEP Hidden',
    },
    {
        'query': 'special_collections:HERMES-INTERNAL-NOTE',
        'name': 'HERMES Internal Notes',
    },
    {
        'query': 'special_collections:LARSOFT-INTERNAL-NOTE',
        'name': 'LARSOFT Internal Notes',
    },
    {
        'query': 'special_collections:LARSOFT-NOTE',
        'name': 'LARSOFT Notes',
    },
    {
        'query': 'special_collections:ZEUS-INTERNAL-NOTE',
        'name': 'ZEUS Internal Notes',
    },
    {
        'query': 'special_collections:ZEUS-PRELIMINARY-NOTE',
        'name': 'ZEUS Preliminary Notes',
    },
]

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

# SEARCH_ELASTIC_KEYWORD_MAPPING -- this variable holds a dictionary to map
# invenio keywords to elasticsearch fields
SEARCH_ELASTIC_KEYWORD_MAPPING = {
    None: ['global_fulltext'],
    "control_number": ["control_number"],
    "author": ["authors.full_name", "authors.alternative_names"],
    "exactauthor": ["exactauthor.raw", "authors.full_name",
                    "authors.alternative_names", "authors.ids.value"
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
    "advisors": ["advisors.name"],
    "title": ["titles.title", "titles.title.raw^2",
              "title_translation.title", "title_variation",
              "title_translation.subtitle", "titles.subtitle"],
    "cnum": ["publication_info.cnum"],
    "980": [
        "collections.primary",
        "collections.secondary",
        "collections.deleted",
    ],
    "980__a": ["collections.primary"],
    "980__b": ["collections.secondary"],
    "542__l": ["information_relating_to_copyright_status.copyright_status"],
    "conf_subject": ["field_code.value"],
    "037__c": ["arxiv_eprints.categories"],
    "246__a": ["titles.title"],
    "595": ["hidden_notes"],
    "650__a": ["inspire_categories.term"],
    "695__a": ["keywords.keyword"],
    "695__e": ["energy_ranges"],
    "773__y": ["publication_info.year"],
    "authorcount": ["authors.full_name"],
    "arxiv": ["arxiv_eprints.value"],
    "caption": ["urls.description"],
    "country": ["authors.affiliations.value"],
    "firstauthor": ["authors.full_name", "authors.alternative_names"],
    "fulltext": ["urls.value"],
    "journal": ["publication_info.recid",
                "publication_info.page_start",
                "publication_info.artid",
                "publication_info.page_range",
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
    "journal_page": ["publication_info.page_start",
                     "publication_info.page_range"
                     "publication_info.artid"],
    "keyword": ["keywords.keyword"],
    "note": ["public_notes.value"],
    "reference": ["references.doi", "references.report_number",
                  "references.journal_pubnote"
                  ],
    "subject": ["inspire_categories.term"],
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
    'datecreated': ['legacy_creation_date'],
    "recid": ["control_number"],
    "cited": ["citation_count"],
    "topcite": ["citation_count"]
}

# Records
# =======
RECORDS_REST_ENDPOINTS = dict(
    literature=dict(
        default_endpoint_prefix=True,
        pid_type='lit',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:LiteratureSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
            'application/x-bibtex': ('inspirehep.modules.records.serializers'
                                     ':bibtex_v1_response'),
            'application/x-orcid': ('invenio_orcid.serializers'
                                    ':orcid_response'),
            'application/x-latexeu': ('inspirehep.modules.records.serializers'
                                      ':latexeu_v1_response'),
            'application/x-latexus': ('inspirehep.modules.records.serializers'
                                      ':latexus_v1_response'),
            'application/x-cvformatlatex': (
                'inspirehep.modules.records.serializers'
                ':cvformatlatex_v1_response'),
            'application/x-cvformathtml': (
                'inspirehep.modules.records.serializers'
                ':cvformathtml_v1_response'),
            'application/x-cvformattext': (
                'inspirehep.modules.records.serializers'
                ':cvformattext_v1_response'),
            'application/x-impact.graph+json': (
                'inspirehep.modules.records.serializers'
                ':impactgraph_v1_response'
            ),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'inspirehep.modules.records.serializers'
                ':json_literature_brief_v1_search'
            ),
            'application/x-bibtex': ('inspirehep.modules.records.serializers'
                                     ':bibtex_v1_search'),
            'application/x-orcid': ('invenio_orcid.serializers'
                                    ':orcid_search'),
            'application/x-latexeu': ('inspirehep.modules.records.serializers'
                                      ':latexeu_v1_search'),
            'application/x-latexus': ('inspirehep.modules.records.serializers'
                                      ':latexus_v1_search'),
            'application/x-cvformatlatex': (
                'inspirehep.modules.records.serializers'
                ':cvformatlatex_v1_search'),
            'application/x-cvformathtml': (
                'inspirehep.modules.records.serializers'
                ':cvformathtml_v1_search'),
            'application/x-cvformattext': (
                'inspirehep.modules.records.serializers'
                ':cvformattext_v1_search'),
        },
        suggesters=dict(
            abstract_source=dict(completion=dict(
                field='abstracts.abstract_source_suggest'
            ))
        ),
        list_route='/literature/',
        item_route=(
            '/literature'
            '/<pid(lit,record_class="inspirehep.modules.records.api:ESRecord"):pid_value>'),
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        read_permission_factory_imp="inspirehep.modules.records.permissions:record_read_permission_factory",
        record_class='inspirehep.modules.records.api:ESRecord'
    ),
    literature_citesummary=dict(
        default_media_type='application/json',
        item_route=(
            '/literature'
            '/<pid(lit,record_class="inspirehep.modules.records.api:ESRecord"):pid_value>'
            '/citesummary'),
        list_route='/literature/',
        max_result_window=10000,
        pid_fetcher='inspire_recid_fetcher',
        pid_minter='inspire_recid_minter',
        pid_type='lit',
        record_serializers={
            'application/json': (
                'inspirehep.modules.api.v1.literature:citesummary_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_class='inspirehep.modules.search:LiteratureSearch',
        search_factory_imp=(
            'inspirehep.modules.search.query:inspire_search_factory'),
        search_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_response')
        },
    ),
    literature_db=dict(
        pid_type='lit',
        search_class='inspirehep.modules.search:LiteratureSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/literature/db',
        item_route='/literature/<pid(lit,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    authors=dict(
        default_endpoint_prefix=True,
        pid_type='aut',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:AuthorsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/authors/',
        item_route='/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
    ),
    authors_db=dict(
        pid_type='aut',
        search_class='inspirehep.modules.search:AuthorsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/authors/db',
        item_route='/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    authors_citations=dict(
        pid_type='aut',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:AuthorsSearch',
        record_serializers={
            'application/json': ('inspirehep.modules.authors.rest'
                                 ':citations_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/authors/',
        item_route='/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/citations',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp=('inspirehep.modules.search.query'
                            ':inspire_search_factory'),
    ),
    authors_citesummary=dict(
        default_media_type='application/json',
        item_route='/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/citesummary',
        list_route='/authors/',
        max_result_window=10000,
        pid_fetcher='inspire_recid_fetcher',
        pid_minter='inspire_recid_minter',
        pid_type='aut',
        record_serializers={
            'application/json': (
                'inspirehep.modules.api.v1.authors:citesummary_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_class='inspirehep.modules.search:AuthorsSearch',
        search_factory_imp=(
            'inspirehep.modules.search.query:inspire_search_factory'),
        search_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers:json_v1_search'),
        },
    ),
    authors_coauthors=dict(
        pid_type='aut',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:AuthorsSearch',
        record_serializers={
            'application/json': ('inspirehep.modules.authors.rest'
                                 ':coauthors_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/authors/',
        item_route='/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/coauthors',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp=('inspirehep.modules.search.query'
                            ':inspire_search_factory'),
    ),
    authors_publications=dict(
        pid_type='aut',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:AuthorsSearch',
        record_serializers={
            'application/json': ('inspirehep.modules.authors.rest'
                                 ':publications_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/authors/',
        item_route='/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/publications',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp=('inspirehep.modules.search.query'
                            ':inspire_search_factory'),
    ),
    authors_stats=dict(
        pid_type='aut',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:AuthorsSearch',
        record_serializers={
            'application/json': ('inspirehep.modules.authors.rest'
                                 ':stats_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/authors/',
        item_route='/authors/<pid(aut,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/stats',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp=('inspirehep.modules.search.query'
                            ':inspire_search_factory'),
    ),
    data=dict(
        default_endpoint_prefix=True,
        pid_type='dat',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:DataSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/data/',
        item_route='/data/<pid(dat,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
    ),
    data_db=dict(
        pid_type='dat',
        search_class='inspirehep.modules.search:DataSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/data/db',
        item_route='/data/<pid(dat,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    conferences=dict(
        default_endpoint_prefix=True,
        pid_type='con',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:ConferencesSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/conferences/',
        item_route='/conferences/<pid(con,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
    ),
    conferences_db=dict(
        pid_type='con',
        search_class='inspirehep.modules.search:ConferencesSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/conferences/db',
        item_route='/conferences/<pid(con,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    jobs=dict(
        default_endpoint_prefix=True,
        pid_type='job',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:JobsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/jobs/',
        item_route='/jobs/<pid(job,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
    ),
    jobs_db=dict(
        pid_type='job',
        search_class='inspirehep.modules.search:JobsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/jobs/db',
        item_route='/jobs/<pid(job,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    institutions=dict(
        default_endpoint_prefix=True,
        pid_type='ins',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:InstitutionsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/institutions/',
        item_route='/institutions/<pid(ins,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
    ),
    institutions_db=dict(
        pid_type='ins',
        search_class='inspirehep.modules.search:InstitutionsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/institutions/db',
        item_route='/institutions/<pid(ins,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    institutions_citesummary=dict(
        default_media_type='application/json',
        item_route=(
            '/institutions/<pid(ins,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/citesummary'),
        list_route='/institutions/',
        max_result_window=10000,
        pid_fetcher='inspire_recid_fetcher',
        pid_minter='inspire_recid_minter',
        pid_type='ins',
        record_serializers={
            'application/json': (
                'inspirehep.modules.api.v1.institutions:citesummary_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_class='inspirehep.modules.search:InstitutionsSearch',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        search_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers:json_v1_search'),
        },
    ),
    experiments=dict(
        default_endpoint_prefix=True,
        pid_type='exp',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:ExperimentsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        suggesters=dict(
            experiment=dict(completion=dict(
                field='experiment_suggest'
            ))
        ),
        list_route='/experiments/',
        item_route='/experiments/<pid(exp,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
    ),
    experiments_db=dict(
        pid_type='exp',
        search_class='inspirehep.modules.search:ExperimentsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/experiments/db',
        item_route='/experiments/<pid(exp,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    experiments_citesummary=dict(
        default_media_type='application/json',
        item_route=(
            '/experiments/<pid(exp,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/citesummary'),
        list_route='/experiments/',
        max_result_window=10000,
        pid_fetcher='inspire_recid_fetcher',
        pid_minter='inspire_recid_minter',
        pid_type='exp',
        record_serializers={
            'application/json': (
                'inspirehep.modules.api.v1.experiments:citesummary_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_class='inspirehep.modules.search:ExperimentsSearch',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        search_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers:json_v1_search'),
        },
    ),
    journals=dict(
        default_endpoint_prefix=True,
        pid_type='jou',
        pid_minter='inspire_recid_minter',
        pid_fetcher='inspire_recid_fetcher',
        search_class='inspirehep.modules.search:JournalsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers'
                ':json_v1_search'
            ),
        },
        list_route='/journals/',
        item_route='/journals/<pid(jou,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
    ),
    journals_db=dict(
        pid_type='jou',
        search_class='inspirehep.modules.search:JournalsSearch',
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response')
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search')
        },
        list_route='/journals/db',
        item_route='/journals/<pid(jou,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/db',
        default_media_type='application/json',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        update_permission_factory_imp="inspirehep.modules.records.permissions:record_update_permission_factory",
    ),
    journals_citesummary=dict(
        default_media_type='application/json',
        item_route=(
            '/journals/<pid(jou,record_class="inspirehep.modules.records.api:InspireRecord"):pid_value>/citesummary'),
        list_route='/journals/',
        max_result_window=10000,
        pid_fetcher='inspire_recid_fetcher',
        pid_minter='inspire_recid_minter',
        pid_type='jou',
        record_serializers={
            'application/json': (
                'inspirehep.modules.api.v1.journals:citesummary_response'),
        },
        record_class='inspirehep.modules.records.api:InspireRecord',
        search_class='inspirehep.modules.search:JournalsSearch',
        search_factory_imp='inspirehep.modules.search.query:inspire_search_factory',
        search_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_search'),
            'application/vnd+inspire.brief+json': (
                'invenio_records_rest.serializers:json_v1_search'),
        },
    ),
)


RECORDS_UI_DEFAULT_PERMISSION_FACTORY = \
    "inspirehep.modules.records.permissions:record_read_permission_factory"

RECORDS_UI_ENDPOINTS = dict(
    literature=dict(
        pid_type='lit',
        route='/literature/<pid_value>',
        template='inspirehep_theme/format/record/'
                 'Inspire_Default_HTML_detailed.tpl',
        record_class='inspirehep.modules.records.wrappers:LiteratureRecord',
    ),
    authors=dict(
        pid_type='aut',
        route='/authors/<pid_value>',
        template='inspirehep_theme/format/record/'
                 'authors/Author_HTML_detailed.html',
        record_class='inspirehep.modules.records.wrappers:AuthorsRecord',
    ),
    data=dict(
        pid_type='dat',
        route='/data/<pid_value>',
        template='inspirehep_theme/format/record/Data_HTML_detailed.tpl'
    ),
    conferences=dict(
        pid_type='con',
        route='/conferences/<pid_value>',
        template='inspirehep_theme/format/record/Conference_HTML_detailed.tpl',
        record_class='inspirehep.modules.records.wrappers:ConferencesRecord',
    ),
    jobs=dict(
        pid_type='job',
        route='/jobs/<pid_value>',
        template='inspirehep_theme/format/record/Job_HTML_detailed.tpl',
        record_class='inspirehep.modules.records.wrappers:JobsRecord',
    ),
    institutions=dict(
        pid_type='ins',
        route='/institutions/<pid_value>',
        template='inspirehep_theme/format/record/Institution_HTML_detailed.tpl',
        record_class='inspirehep.modules.records.wrappers:InstitutionsRecord',
    ),
    experiments=dict(
        pid_type='exp',
        route='/experiments/<pid_value>',
        template='inspirehep_theme/format/record/Experiment_HTML_detailed.tpl',
        record_class='inspirehep.modules.records.wrappers:ExperimentsRecord',
    ),
    journals=dict(
        pid_type='jou',
        route='/journals/<pid_value>',
        template='inspirehep_theme/format/record/Journal_HTML_detailed.tpl',
        record_class='inspirehep.modules.records.wrappers:JournalsRecord',
    )
)

RECORDS_REST_FACETS = {
    "records-hep": {
        "filters": {
            "author": terms_filter('exactauthor.raw'),
            "subject": terms_filter('facet_inspire_subjects'),
            "doc_type": terms_filter('facet_inspire_doc_type'),
            "formulas": terms_filter('facet_formulas'),
            "experiment": terms_filter(
                'accelerator_experiments.facet_experiment'),
            "earliest_date": range_filter(
                'earliest_date',
                format='yyyy',
                end_date_math='/y')
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
                    "field": "facet_authors",
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
                    "format": "yyyy",
                    "min_doc_count": 1,
                    "order": {"_count": "desc"}
                }
            }
        }
    },
    "records-authors": {
        "filters": {
            "inspire_categories": terms_filter('inspire_categories.term'),
            "institution": terms_filter('positions.institution.name')
        },
        "aggs": {
            "inspire_categories": {
                "terms": {
                    "field": "inspire_categories.term",
                    "size": 20
                }
            },
            "institution": {
                "terms": {
                    "field": "positions.institution.name",
                    "size": 20
                }
            }
        }
    },
    "records-conferences": {
        "filters": {
            "series": terms_filter('series'),
            "inspire_categories": terms_filter('inspire_categories.term')
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
                    "min_doc_count": 1,
                    "order": {"_count": "desc"}
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
                    "field": "continent",
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
        "query": "-bestmatch",
        "noquery": "-mostrecent"
    },

    "records-data": {
        "query": "relevance",
        "noquery": "latest"
    },

    "records-jobs": {
        "query": "bestmatch",
        "noquery": "-mostrecent"
    }
}

RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY = None

RECORDS_VALIDATION_TYPES = {
    'array': (list, tuple),
}

JSONSCHEMAS_HOST = "localhost:5000"
JSONSCHEMAS_REPLACE_REFS = True
JSONSCHEMAS_LOADER_CLS = 'inspirehep.modules.records.json_ref_loader.SCHEMA_LOADER_CLS'

INDEXER_DEFAULT_INDEX = "records-hep"
INDEXER_DEFAULT_DOC_TYPE = "hep"
INDEXER_REPLACE_REFS = False
INDEXER_BULK_REQUEST_TIMEOUT = float(120)

# OAuthclient
# ===========
orcid.REMOTE_APP['params']['request_token_params'] = {'scope': '/orcid-profile/read-limited /activities/update /orcid-bio/update'}
OAUTHCLIENT_REMOTE_APPS = dict(
    orcid=orcid.REMOTE_APP,
)
OAUTHCLIENT_ORCID_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

OAUTHCLIENT_SETTINGS_TEMPLATE = 'inspirehep_theme/page.html'

ORCID_SYNCHRONIZATION_ENABLED = False

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

# Web services and APIs
# =====================
BEARD_API_URL = None  # e.g. "http://beard.inspirehep.net/api"
MAGPIE_API_URL = "http://magpie.inspirehep.net/api"

# Harvesting and Workflows
# ========================
ARXIV_PDF_URL = "http://arxiv.org/pdf/{arxiv_id}"
ARXIV_TARBALL_URL = "http://arxiv.org/e-print/{arxiv_id}"

WORKFLOWS_DEFAULT_FILE_LOCATION_NAME = "holdingpen"
"""Name of default workflow Location reference."""

WORKFLOWS_OBJECT_CLASS = "invenio_workflows_files.api.WorkflowObject"
"""Enable obj.files API."""

WORKFLOWS_UI_BASE_TEMPLATE = BASE_TEMPLATE
WORKFLOWS_UI_INDEX_TEMPLATE = "inspire_workflows/index.html"
WORKFLOWS_UI_LIST_TEMPLATE = "inspire_workflows/list.html"
WORKFLOWS_UI_DETAILS_TEMPLATE = "inspire_workflows/details.html"
WORKFLOWS_UI_LIST_ROW_TEMPLATE = "inspire_workflows/list_row.html"

WORKFLOWS_UI_URL = "/holdingpen"
WORKFLOWS_UI_API_URL = "/api/holdingpen/"

WORKFLOWS_UI_REST_ENDPOINT = dict(
    workflow_object_serializers={
        'application/json': ('invenio_workflows_ui.serializers'
                             ':json_serializer'),
    },
    search_serializers={
        'application/json': ('invenio_workflows_ui.serializers'
                             ':json_search_serializer')
    },
    action_serializers={
        'application/json': ('invenio_workflows_ui.serializers'
                             ':json_action_serializer'),
    },
    bulk_action_serializers={
        'application/json': ('invenio_workflows_ui.serializers'
                             ':json_action_serializer'),
    },
    file_serializers={
        'application/json': ('invenio_workflows_ui.serializers'
                             ':json_file_serializer'),
    },
    list_route='/holdingpen/',
    item_route='/holdingpen/<object_id>',
    file_list_route='/holdingpen/<object_id>/files',
    file_item_route='/holdingpen/<object_id>/files/<path:key>',
    search_index='holdingpen',
    search_factory_imp=('inspirehep.modules.workflows.search'
                        ':holdingpen_search_factory'),
    default_media_type='application/json',
    max_result_window=10000,
)

WORKFLOWS_UI_DATA_TYPES = dict(
    hep=dict(
        search_index='holdingpen-hep',
        search_type='hep',
    ),
    authors=dict(
        search_index='holdingpen-authors',
        search_type='authors',
    ),
)

WORKFLOWS_UI_REST_FACETS = {
    "holdingpen": {
        "filters": {
            "status": terms_filter('_workflow.status'),
            "source": terms_filter('metadata.acquisition_source.method'),
            "workflow_name": terms_filter('_workflow.workflow_name'),
            "is-update": terms_filter('_extra_data.is-update'),
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
                    "field": "metadata.acquisition_source.method",
                    "size": 20
                }
            },
            "workflow_name": {
                "terms": {
                    "field": "_workflow.workflow_name",
                    "size": 20
                }
            },
        }
    }
}

WORKFLOWS_UI_REST_SORT_OPTIONS = {
    "holdingpen": {
        "bestmatch": {
            "title": 'Best match',
            "fields": ['_score'],
            "default_order": 'desc',
            "order": 1,
        },
        "mostrecent": {
            "title": 'Most recent',
            "fields": ['_workflow.modified'],
            "default_order": 'desc',
            "order": 2,
        },
    },
}

WORKFLOWS_UI_REST_DEFAULT_SORT = {
    "holdingpen": {
        "query": "-bestmatch",
        "noquery": "-mostrecent"
    }
}

AUTHORS_UPDATE_BASE_URL = "http://inspirehep.net"

# Crawling
# ========

CRAWLER_HOST_URL = "http://localhost:6800"

CRAWLER_SETTINGS = {
    # URL to your flower instance
    "API_PIPELINE_URL": "http://localhost:5555/api/task/async-apply",
    "API_PIPELINE_TASK_ENDPOINT_DEFAULT": "inspire_crawler.tasks.submit_results",
}

# OrcID configuration
# ================

ORCID_JSON_CONVERTER_MODULE = 'inspirehep.modules.orcid.utils:convert_to_orcid'
ORCID_ID_FETCHER = 'inspirehep.modules.orcid.utils:get_orcid_id'

ORCID_AUTHORS_SEARCH_CLASS = 'inspirehep.modules.search:AuthorsSearch'

ORCID_RECORDS_PID_TYPE = 'lit'
ORCID_RECORDS_DOC_TYPE = 'hep'
ORCID_RECORDS_PID_FETCHER = 'inspire_recid_fetcher'

ORCID_WORK_TYPES = {
    "book": "BOOK",
    "conferencepaper": "CONFERENCE_PAPER",
    "proceedings": "BOOK",
    "preprint": "WORKING_PAPER",
    "note": "WORKING_PAPER",
    "published": "JOURNAL_ARTICLE",
    "thesis": "DISSERTATION",
    "lectures": "LECTURE_SPEECH",
    "bookchapter": "BOOK_CHAPTER",
    "report": "REPORT"
}


# Inspire mappings
# ================

INSPIRE_LEGACY_ROLES = {
    'editing': [
        'ed.',
        'eds.',
        'ed,,',
        'eds',
        'ed,',
        'ed. et al.'
    ],
    'administration': [
        'task force leader',
        'resource manager',
        'scientific coordinator',
        'chairman',
        'chair',
        'workshop chair'
    ]
}

INSPIRE_LICENSE_TYPES = [
    'CC-BY',
    'CC-BY-NC',
    'CC-BY-NC-ND',
    'CC-BY-NC-SA',
    'CC-BY-ND',
    'CC-BY-SA',
    'Other'
]

INSPIRE_RANK_TYPES = {
    'STAFF': {},
    'SENIOR': {},
    'JUNIOR': {},
    'VISITOR': {
        'alternative_names': ['VISITING SCIENTIST'],
    },
    'POSTDOC': {
        'abbreviations': ['PD']
    },
    'PHD': {
        'alternative_names': ['STUDENT']
    },
    'MASTER': {
        'abbreviations': ['MAS', 'MS', 'MSC']
    },
    'UNDERGRADUATE': {
        'alternative_names': ['BACHELOR'],
        'abbreviations': ['UG', 'BS', 'BA', 'BSC']
    }
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
        'related_experiments.record',
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
        'succeding_entry.record',
        'thesis.institutions.record',
        'thesis_supervisors.affiliations.record',
    ],
    'institutions': [
        'related_institutes.record',
    ],
    'jobs': [
        'experiments.record',
        'institutions.record',
    ],
    'journals': [
        'relation.record',
    ],
}
"""Controls which fields are updated when the referred record is updated."""
