#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

"""
INSPIRE configuration
--------------------
Instance independent configuration (e.g. which extensions to load) is defined
in ``inspire.config'' while instance dependent configuration (e.g. database
host etc.) is defined in an optional ``inspire.instance_config'' which
can be installed by a separate package.

This config module is loaded by the Flask application factory via an entry
point specified in the setup.py::

    entry_points={
        'invenio.config': [
            "inspire = inspire.config"
        ]
    },
"""

EXTENSIONS = [
    'invenio.ext.arxiv:Arxiv',
    'invenio.ext.crossref:CrossRef',
    'invenio.ext.confighacks',
    'invenio.ext.jinja2hacks',
    'invenio.ext.debug_toolbar',
    'invenio.ext.babel',
    'invenio.ext.sqlalchemy',
    'invenio.ext.sslify',
    'invenio.ext.cache',
    'invenio.ext.session',
    'invenio.ext.login',
    'invenio.ext.principal',
    'invenio.ext.email',
    'invenio.ext.legacy',
    'invenio.ext.assets',
    'invenio.ext.template',
    'invenio.ext.admin',
    'invenio.ext.logging',
    'invenio.ext.logging.backends.fs',
    'invenio.ext.logging.backends.legacy',
    'invenio.ext.logging.backends.sentry',
    'invenio.ext.gravatar',
    'invenio.ext.collect',
    'invenio.ext.restful',
    'invenio.ext.mixer',
    'flask.ext.menu:Menu',
    'flask.ext.breadcrumbs:Breadcrumbs',
    'invenio.modules.deposit.url_converters',
    'inspire.ext.search_bar',
    'inspire.ext.formatter_jinja_filters',
]

PACKAGES = [
    'inspire.base',
    'inspire.demosite',
    'inspire.ext',
    'inspire.utils',
    'inspire.modules.workflows',
    'inspire.modules.deposit',
    'inspire.modules.access',
    'invenio.modules.access',
    'invenio.modules.accounts',
    'invenio.modules.alerts',
    'invenio.modules.apikeys',
    'invenio.modules.authorids',
    'invenio.modules.authorprofiles',
    'invenio.modules.baskets',
    'invenio.modules.bulletin',
    'invenio.modules.circulation',
    'invenio.modules.classifier',
    'invenio.modules.cloudconnector',
    'invenio.modules.comments',
    'invenio.modules.communities',
    'invenio.modules.converter',
    'invenio.modules.dashboard',
    'invenio.modules.deposit',
    'invenio.modules.documentation',
    'invenio.modules.documents',
    'invenio.modules.editor',
    'invenio.modules.encoder',
    'invenio.modules.exporter',
    'invenio.modules.formatter',
    'invenio.modules.groups',
    'invenio.modules.indexer',
    'invenio.modules.jsonalchemy',
    'invenio.modules.knowledge',
    'invenio.modules.linkbacks',
    'invenio.modules.matcher',
    'invenio.modules.merger',
    'invenio.modules.messages',
    'invenio.modules.oaiharvester',
    'invenio.modules.oairepository',
    'invenio.modules.oauth2server',
    'invenio.modules.oauthclient',
    'invenio.modules.pidstore',
    'invenio.modules.previewer',
    'invenio.modules.ranker',
    'invenio.modules.records',
    'invenio.modules.redirector',
    'invenio.modules.refextract',
    'invenio.modules.scheduler',
    'invenio.modules.search',
    'invenio.modules.sequencegenerator',
    'invenio.modules.sorter',
    'invenio.modules.statistics',
    'invenio.modules.submit',
    'invenio.modules.sword',
    'invenio.modules.tags',
    'invenio.modules.textminer',
    'invenio.modules.tickets',
    'invenio.modules.upgrader',
    'invenio.modules.uploader',
    'invenio.modules.webhooks',
    'invenio.modules.workflows',
    'invenio.modules.pages',
    'invenio.base',
]

PACKAGES_EXCLUDE = [
    'invenio.modules.archiver',
    'invenio.modules.annotations',
    'invenio.modules.communities',
    'invenio.modules.linkbacks',
    'invenio.modules.multimedia',
]

# Configuration related to Deposit module

DEPOSIT_TYPES = [
    'inspire.modules.deposit.workflows.literature.literature',
    'inspire.modules.deposit.workflows.literature_simple.literature_simple',
]
DEPOSIT_DEFAULT_TYPE = "inspire.modules.deposit.workflows.literature:literature"

# facets ignored by auto-discovery service, they are not accessible in inspire
PACKAGES_FACETS_EXCLUDE = [
    'invenio.modules.search.facets.collection',
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
    langs[lang] = u"INSPIRE - High-Energy Physics Information System"
CFG_SITE_NAME_INTL = langs

# Rename blueprint prefixes

BLUEPRINTS_URL_PREFIXES = {'webdeposit': '/submit'}

# Flask specific configuration - This prevents from getting "MySQL server
# has gone away" error

SQLALCHEMY_POOL_RECYCLE = 700

# OAUTH configuration

OAUTHCLIENT_REMOTE_APPS = dict(
    orcid=dict(
        title='ORCID',
        description='Connecting Research and Researchers.',
        icon='',
        authorized_handler="invenio.modules.oauthclient.handlers"
                           ":authorized_signup_handler",
        disconnect_handler="invenio.modules.oauthclient.handlers"
                           ":disconnect_handler",
        signup_handler=dict(
            info="invenio.modules.oauthclient.contrib.orcid:account_info",
            setup="invenio.modules.oauthclient.contrib.orcid:account_setup",
            view="invenio.modules.oauthclient.handlers:signup_handler",
        ),
        params=dict(
            request_token_params={'scope': '/authenticate'},
            base_url='https://pub.orcid.com/',
            request_token_url=None,
            access_token_url="https://pub.orcid.org/oauth/token",
            access_token_method='POST',
            authorize_url="https://orcid.org/oauth/authorize#show_login",
            app_key="ORCID_APP_CREDENTIALS",
            content_type="application/json",
        )
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

# For production only, instance_config contains configuration of
# database credentials and other instance specific configuration
try:
    from inspire.instance_config import *
except ImportError:
    pass
