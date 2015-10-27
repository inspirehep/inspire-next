# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""
INSPIRE configuration
---------------------

This config module is loaded by the Flask application factory via an entry
point specified in the setup.py::

    entry_points={
        'invenio.config': [
            "inspire = inspire.config"
        ]
    },
"""

from invenio_query_parser.contrib.spires.walkers.pypeg_to_ast import PypegConverter
from invenio_query_parser.contrib.spires.walkers.spires_to_invenio import SpiresToInvenio


EXTENSIONS = [
    'invenio_ext.confighacks',
    'invenio_ext.passlib:Passlib',
    'invenio_ext.debug_toolbar',
    'invenio_ext.babel',
    'invenio_ext.sqlalchemy',
    'invenio_ext.sslify',
    'invenio_ext.cache',
    'invenio_ext.session',
    'invenio_ext.login',
    'invenio_ext.principal',
    'invenio_ext.email',
    'invenio_ext.fixtures',  # before legacy
    'invenio_ext.legacy',
    'invenio_ext.assets',
    'invenio_ext.template',
    'invenio_ext.admin',
    'invenio_ext.logging',
    'invenio_ext.logging.backends.fs',
    'invenio_ext.logging.backends.legacy',
    'invenio_ext.logging.backends.sentry',
    'invenio_ext.gravatar',
    'invenio_ext.collect',
    'invenio_ext.restful',
    'invenio_ext.menu',
    'invenio_ext.jasmine',  # after assets
    'flask_breadcrumbs:Breadcrumbs',
    'invenio_deposit.url_converters',
    'invenio_ext.arxiv:Arxiv',
    'invenio_ext.crossref:CrossRef',
    'invenio_ext.es',
    'invenio_ext.mixer',
    'inspire.ext.search_bar',
    'inspire.ext.formatter_jinja_filters',
    'inspire.ext.deprecation_warnings:disable_deprecation_warnings',
]

PACKAGES = [
    'inspire.base',
    'inspire.demosite',
    'inspire.dojson',
    'inspire.utils',
    'inspire.modules.*',
    'invenio_celery',
    'invenio_classifier',
    'invenio_oaiharvester',
    'invenio_grobid',
    'invenio_records',
    'invenio_search',
    'invenio_collections',
    'invenio_documents',
    'invenio_pidstore',
    'invenio_formatter',
    'invenio_unapi',
    'invenio_webhooks',
    'invenio_deposit',
    'invenio_workflows',
    'invenio_knowledge',
    'invenio_oauthclient',
    'invenio_oauth2server',
    'invenio_groups',
    'invenio_access',
    'invenio_accounts',
    'invenio_upgrader',
    'invenio_testing',
    'invenio_base'
]

# Configuration related to Deposit module

DEPOSIT_TYPES = [
    'inspire.modules.deposit.workflows.literature.literature',
    'inspire.modules.deposit.workflows.literature_simple.literature_simple',
]
DEPOSIT_DEFAULT_TYPE = "inspire.modules.deposit.workflows.literature:literature"

# facets ignored by auto-discovery service, they are not accessible in inspire
PACKAGES_FACETS_EXCLUDE = [
    'invenio_search.facets.collection',
]


SEARCH_QUERY_PARSER = 'invenio_query_parser.contrib.spires.parser:Main'

SEARCH_QUERY_WALKERS = [
    PypegConverter,
    SpiresToInvenio,
]

# Task queue configuration


CELERY_RESULT_BACKEND = "amqp://guest:guest@localhost:5672//"
CELERY_ACCEPT_CONTENT = ["msgpack"]

BROKER_URL = "amqp://guest:guest@localhost:5672//"

# Site name configuration

CFG_SITE_LANG = u"en"
CFG_SITE_LANGS = ['en', ]

# CFG_SITE_NAME and main collection name should be the same for empty search
# to work
CFG_SITE_NAME = u"HEP"

# Logs
CFG_APACHE_LOGDIR = "/var/log/httpd"

# a working mode when the server cooperates with inspirehep.net database
PRODUCTION_MODE = False
CFG_INSPIRE_SITE = 1

langs = {}
for lang in CFG_SITE_LANGS:
    langs[lang] = u"INSPIRE Labs"
CFG_SITE_NAME_INTL = langs

# Rename blueprint prefixes

BLUEPRINTS_URL_PREFIXES = {'webdeposit': '/submit'}

# Flask specific configuration - This prevents from getting "MySQL server
# has gone away" error

SQLALCHEMY_POOL_RECYCLE = 60

DEPRECATION_WARNINGS_PRODUCTION_ENABLED = False

# OAUTH configuration

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
            authorize_url="https://orcid.org/oauth/authorize#show_login",
            app_key="ORCID_APP_CREDENTIALS",
            content_type="application/json",
        ),
        remember=True
    ),
)

ORCID_APP_CREDENTIALS = dict(
    consumer_key="changeme",
    consumer_secret="changeme",
)

CFG_WEBSEARCH_SYNONYM_KBRS = {
    'journal': ['JOURNALS', 'leading_to_comma'],
    'collection': ['COLLECTION', 'exact'],
    'subject': ['SUBJECT', 'exact'],
}

# DOI and arXiv id database search prefixes
CROSSREF_SEARCH_PREFIX = u"doi:"
ARXIV_SEARCH_PREFIX = u"035__a:oai:arXiv.org:"

# remember_me cookie set by Flask-Login should be marked as secure
# or Invenio will crash when using http

REMEMBER_COOKIE_SECURE = True

# Inspire specific config

INSPIRE_EMAIL_REGEX = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
INSPIRE_URL_REGEX = "^(?:http(?:s)?:\/\/)?(?:www\.)?(?:[\w-]*)\.\w{2,}$"

# year - month (2 digits) -day (2 digits)
INSPIRE_DATE_REGEX = "^[1|2][0-9]{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0|1])$"

INSPIRE_YEAR_MIN = 1000
INSPIRE_YEAR_MAX = 2050

INSPIRE_ARXIV_CATEGORIES = ['acc-phys', 'astro-ph', 'atom-ph', 'chao-dyn',
                            'climate', 'comp', 'cond-mat', 'genl-th', 'gr-qc',
                            'hep-ex', 'hep-lat', 'hep-ph', 'hep-th', 'instr',
                            'librarian', 'math', 'math-ph', 'med-phys', 'nlin',
                            'nucl-ex', 'nucl-th', 'physics', 'plasma-phys',
                            'q-bio', 'quant-ph', 'ssrl', 'other']

INSPIRE_CATEGORIES_SOURCES = ['arxiv']
INSPIRE_ACCEPTED_CATEGORIES = ["hep-th", "hep-ph", "hep-lat", "hep-ex", "nucl-th",
                               "nucl-ex", "physics.acc-ph", "gr-qc", "physics.ins-det",
                               "astro-ph.co", "astro-ph.he"]

OAIHARVESTER_RECORD_ARXIV_ID_LOOKUP = "arxiv_eprints.value"
WORKFLOWS_HOLDING_PEN_DEFAULT_OUTPUT_FORMAT = "hp"

# Harvester config
HARVESTER_WORKFLOWS = {
    "world_scientific": "inspire.modules.harvester.workflows.world_scientific:world_scientific"
}
HARVESTER_WORKFLOWS_CONFIG = {
    "world_scientific": {}
    # Specify special config locally.
    # Expected params: ftp_server, ftp_netrc_file and recipients
}

# DoJSON configuration
RECORD_PROCESSORS = {
    'json': 'json.load',
    'marcxml': 'inspire.dojson.processors:convert_marcxml',
}
RECORDS_BREADCRUMB_TITLE_KEY = 'breadcrumb_title'

# SEARCH_ELASTIC_KEYWORD_MAPPING -- this variable holds a dictionary to map
# invenio keywords to elasticsearch fields
SEARCH_ELASTIC_KEYWORD_MAPPING = {
    "author": {
        'a': ["authors.full_name"],
        'p': ["authors.full_name"],
        'e': ['exactauthor.raw'],
    },
    "abstract": ["abstracts.value"],
    "collection": ["_collections"],
    "affiliation": ["authors.affiliations.value"],
    "reportnumber": ["report_numbers.value"],
    "experiment": ["accelerator_experiments.experiment"],
    "title": ["titles.title"],
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
}

SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING = {
    "HEP": "hep",
    "Conferences": "conferences",
    "Institutions": "institutions",
    "Experiments": "experiments",
    "Jobs": "jobs",
    "Jobs Hidden": "jobshidden",
    "Journals": "journals",
    "HepNames": "authors"
}

SEARCH_ELASTIC_DEFAULT_INDEX = 'hep'
