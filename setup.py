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

"""The next version of INSPIRE."""

from __future__ import absolute_import, division, print_function

import os

from setuptools import find_packages, setup


URL = 'https://github.com/inspirehep/inspire-next'

g = {}
with open(os.path.join('inspirehep', 'version.py'), 'rt') as f:
    exec(f.read(), g)
    version = g['__version__']

readme = open('README.rst').read()

setup_requires = []

install_requires = [
    'Babel~=2.0,>=2.5.1',
    'Flask-Breadcrumbs~=0.0,>=0.4.0',
    'Flask-CeleryExt~=0.0,>=0.3.0',
    'Flask-Gravatar~=0.0,>=0.4.2',
    'Flask-Login~=0.0,>=0.4.0',
    'Flask~=0.0,>=0.12.2',
    'IDUtils~=0.0,>=0.2.4',
    'SQLAlchemy~=1.0,>=1.1.14,<1.2',
    'amqp~=1.0,>=1.4.9',
    'backoff~=1.0,>=1.4.3',
    'backports.tempfile>=1.0rc1',
    'beard~=0.0,>=0.2.0',
    'celery~=3.0,>=3.1.25',
    'elasticsearch-dsl~=2.0,>=2.2.0',
    'elasticsearch~=2.0,>=2.4.1',
    'flask-shell-ipython~=0.0,>=0.3.0',
    'fs~=0.0,>=0.5.4',
    'inspire-crawler~=1.0',
    'inspire-dojson~=57.0,>=57.0.3',
    'inspire-json-merger~=6.0,>=6.0.1',
    'inspire-matcher~=3.0,>=3.0.0',
    'inspire-query-parser~=2.0,>=2.0.0',
    'inspire-schemas~=56.0,>=56.0.3',
    'inspire-utils~=1.0,>=1.0.0',
    'invenio-access>=1.0.0b1',
    'invenio-accounts>=1.0.0b10',
    'invenio-admin>=1.0.0b4',
    'invenio-assets>=1.0.0b7',
    'invenio-base>=1.0.0a16',
    'invenio-cache>=1.0.0b1',
    'invenio-celery>=1.0.0b3',
    'invenio-classifier~=1.0,>=1.3.1',
    'invenio-collections>=1.0.0a4',
    'invenio-config>=1.0.0b3',
    'invenio-db[postgresql,versioning]>=1.0.0b8',
    'invenio-files-rest>=1.0.0a20',
    'invenio-indexer>=1.0.0a10',
    'invenio-jsonschemas>=1.0.0a5',
    'invenio-logging>=1.0.0b3',
    'invenio-mail>=1.0.0b1',
    'invenio-oauthclient>=1.0.0b2',
    'invenio-records-files>=1.0.0a9',
    'invenio-records-rest>=1.0.0b1',
    'invenio-records-ui>=1.0.0b1',
    'invenio-records>=1.0.0b3',
    'invenio-rest[cors]>=1.0.0b1',
    'invenio-search>=1.0.0a11',
    'invenio-userprofiles>=1.0.0b1',
    'invenio-workflows-files~=1.0',
    'invenio-workflows-ui~=2.0',
    'invenio-workflows~=7.0',
    'langdetect~=1.0,>=1.0.7',
    'librabbitmq~=1.0,>=1.6.1',
    'orcid~=0.0,>=0.7.0',
    'plotextractor~=0.0,>=0.1.6',
    'pybtex~=0.0,>=0.21',
    'python-redis-lock~=3.0,>=3.2.0',
    'raven[flask]~=6.0,>=6.2.1',
    'refextract~=0.0,>=0.2.2',
    'requests~=2.0,>=2.18.4',
    'setproctitle~=1.0,>=1.1.10',
    'timeout-decorator~=0.0,>=0.4.0',
    'workflow~=2.0,>=2.1.3',
]

docs_require = [
    'Sphinx~=1.0,>=1.5.6,<1.6',
]

tests_require = [
    'flake8-future-import~=0.0,>=0.4.3',
    'mock~=2.0,>=2.0.0',
    'pytest-cov~=2.0,>=2.5.1',
    'pytest-flake8~=0.0,>=0.9',
    'pytest-selenium~=1.0,>=1.11.1',
    'pytest~=3.0,>=3.3.0',
    'requests_mock~=1.0,>=1.3.0',
]

extras_require = {
    'build-node': [
        'ipdb~=0.0,>=0.10.3',
    ],
    'crawler-node': [
        'hepcrawl~=5.0,>=5.0',
    ],
    'docs': docs_require,
    'tests': tests_require,
    'web-node': [
        'gunicorn~=19.0,>=19.7.1',
    ],
    'worker-node': [
        'flower~=0.0,>=0.9.2',
        'superlance~=1.0,>=1.0.0',
    ],
    'xrootd': [
        'invenio-xrootd>=1.0.0a5',
        'xrootdpyfs~=0.0,>=0.1.5',
    ],
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ['xrootd']:
        continue
    extras_require['all'].extend(reqs)

packages = find_packages(exclude=['docs'])

setup(
    name='Inspirehep',
    version=version,
    url=URL,
    license='GPLv3',
    author='CERN',
    author_email='admin@inspirehep.net',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    description=__doc__,
    long_description=readme,
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'inspirehep = inspirehep.cli:cli',
        ],
        'invenio_access.actions': [
            'admin_holdingpen_authors = inspirehep.modules.authors.permissions:action_admin_holdingpen_authors',
            'editor_use_api = inspirehep.modules.editor.permissions:action_editor_use_api',
            'update_collection = inspirehep.modules.records.permissions:action_update_collection',
            'view_restricted_collection = inspirehep.modules.records.permissions:action_view_restricted_collection',
        ],
        'invenio_assets.bundles': [
            'almondjs = inspirehep.modules.theme.bundles:almondjs',
            'inspirehep_author_profile_js = inspirehep.modules.authors.bundles:js',
            'inspirehep_author_update_css = inspirehep.modules.authors.bundles:update_css',
            'inspirehep_authors_update_form_js = inspirehep.modules.authors.bundles:updatejs',
            'inspirehep_detailed_js = inspirehep.modules.theme.bundles:detailedjs',
            'inspirehep_editor_js = inspirehep.modules.editor.bundles:js',
            'inspirehep_forms_css = inspirehep.modules.forms.bundles:css',
            'inspirehep_forms_js = inspirehep.modules.forms.bundles:js',
            'inspirehep_holding_css = inspirehep.modules.theme.bundles:holding_pen_css',
            'inspirehep_holding_js = inspirehep.modules.workflows.bundles:details_js',
            'inspirehep_landing_page_css = inspirehep.modules.theme.bundles:landing_page_css',
            'inspirehep_literaturesuggest_js = inspirehep.modules.literaturesuggest.bundles:js',
            'inspirehep_theme_css = inspirehep.modules.theme.bundles:css',
            'inspirehep_theme_js = inspirehep.modules.theme.bundles:js',
            'inspirehep_tools_authorlist_js = inspirehep.modules.tools.bundles:js',
            'invenio_search_ui_search_js = inspirehep.modules.search.bundles:js',
            'requirejs = inspirehep.modules.theme.bundles:requirejs',
        ],
        'invenio_base.api_apps': [
            'inspire_search = inspirehep.modules.search:InspireSearch',
            'inspire_theme = inspirehep.modules.theme:INSPIRETheme',
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
            'invenio_collections = invenio_collections:InvenioCollections',
        ],
        'invenio_base.api_blueprints': [
            'inspirehep_editor = inspirehep.modules.editor:blueprint_api',
        ],
        'invenio_base.apps': [
            'inspire_arxiv = inspirehep.modules.arxiv:InspireArXiv',
            'inspire_authors = inspirehep.modules.authors:InspireAuthors',
            'inspire_crossref = inspirehep.modules.crossref:InspireCrossref',
            'inspire_fixtures = inspirehep.modules.fixtures:InspireFixtures',
            'inspire_forms = inspirehep.modules.forms:InspireForms',
            'inspire_hal = inspirehep.modules.hal:InspireHAL',
            'inspire_literaturesuggest = inspirehep.modules.literaturesuggest:InspireLiteratureSuggest',
            'inspire_migrator = inspirehep.modules.migrator:InspireMigrator',
            'inspire_search = inspirehep.modules.search:InspireSearch',
            'inspire_theme = inspirehep.modules.theme:INSPIRETheme',
            'inspire_tools = inspirehep.modules.tools:InspireTools',
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
        ],
        'invenio_base.blueprints': [
            'inspirehep_editor = inspirehep.modules.editor:blueprint',
        ],
        'invenio_celery.tasks': [
            'inspire_migrator = inspirehep.modules.migrator.tasks',
            'inspire_records = inspirehep.modules.records.tasks',
            'inspire_refextract = inspirehep.modules.refextract.tasks',
        ],
        'invenio_db.alembic': [
            'inspirehep = inspirehep:alembic',
        ],
        'invenio_db.models': [
            'inspire_workflows_audit = inspirehep.modules.workflows.models',
        ],
        'invenio_jsonschemas.schemas': [
            'inspire_records = inspire_schemas',
        ],
        'invenio_pidstore.fetchers': [
            'inspire_recid_fetcher = inspirehep.modules.pidstore.fetchers:inspire_recid_fetcher',
        ],
        'invenio_pidstore.minters': [
            'inspire_recid_minter = inspirehep.modules.pidstore.minters:inspire_recid_minter',
        ],
        'invenio_search.mappings': [
            'holdingpen = inspirehep.modules.workflows.mappings',
            'records = inspirehep.modules.records.mappings',
        ],
        'invenio_workflows.workflows': [
            'article = inspirehep.modules.workflows.workflows:Article',
            'author = inspirehep.modules.workflows.workflows:Author',
            'manual_merge = inspirehep.modules.workflows.workflows:ManualMerge',
        ],
        'invenio_workflows_ui.actions': [
            'author_approval = inspirehep.modules.workflows.actions.author_approval:AuthorApproval',
            'hep_approval = inspirehep.modules.workflows.actions.hep_approval:HEPApproval',
            'merge_approval = inspirehep.modules.workflows.actions.merge_approval:MergeApproval',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
