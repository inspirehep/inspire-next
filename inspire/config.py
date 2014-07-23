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

from invenio.base.config import EXTENSIONS as ORIG_EXTENSIONS
from invenio.base.config import CFG_SITE_LANGS

EXTENSIONS = ORIG_EXTENSIONS + [
    'inspire.ext.search_bar',
    'inspire.ext.formatter_jinja_filters'
]

PACKAGES = [
    'inspire.base',
    'inspire.ext',
    'inspire.modules.workflows',
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
    'invenio.base',
]


CELERY_RESULT_BACKEND = "amqp://guest:guest@localhost:5672//"
BROKER_URL = "amqp://guest:guest@localhost:5672//"

CFG_SITE_LANG = u"en"
CFG_SITE_LANGS = ['en', ]


# CFG_SITE_NAME and main collection name should be the same for empty search
# to work
CFG_SITE_NAME = u"HEP"

langs = {}
for lang in CFG_SITE_LANGS:
    langs[lang] = u"INSPIRE - High-Energy Physics Literature Database"
CFG_SITE_NAME_INTL = langs

try:
    from inspire.instance_config import *
except ImportError:
    pass
