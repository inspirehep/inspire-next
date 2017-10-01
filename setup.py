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

"""INSPIRE is the leading information platform for HEP literature."""

from __future__ import absolute_import, division, print_function

import os

from setuptools import find_packages, setup


readme = open('README.rst').read()

install_requires = [
    'Babel~=2.0,>=2.5.1',
    'Flask-Breadcrumbs~=0.0,>=0.4.0',
    'Flask-CeleryExt~=0.0,>=0.3.0',
    'Flask-Gravatar~=0.0,>=0.4.2',
    'Flask-Login~=0.0,>=0.4.0',
    'Flask~=0.0,>=0.12.2',
    'IDUtils~=0.0,>=0.2.4',
    'SQLAlchemy~=1.0,>=1.0.19,<1.1',
    'amqp~=1.0,>=1.4.9',
    'backoff~=1.0,>=1.4.3',
    'backports.tempfile>=1.0rc1',
    'beard~=0.0,>=0.2.0',
    'celery~=3.0,>=3.1.25',
    'elasticsearch-dsl~=2.0,>=2.1.0,<2.2.0',
    'elasticsearch~=2.0,>=2.4.1',
    'flask-shell-ipython~=0.0,>=0.3.0',
    'inspire-crawler~=0.0,>=0.4.2',
    'inspire-dojson~=49.0,>=49.0.4',
    'inspire-query-parser~=0.0,>=0.2.7',
    'inspire-schemas~=49.0,>=49.0.0',
    'inspire-utils~=0.0,>=0.0.8',
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
    'invenio-records>=1.0.0b2',
    'invenio-rest[cors]>=1.0.0b1',
    'invenio-search>=1.0.0a10',
    'invenio-userprofiles>=1.0.0b1',
    'invenio-workflows-files~=0.0,>=0.0.6',
    'invenio-workflows-ui~=1.0,>=1.1.1',
    'invenio-workflows~=6.0,>=6.1.0',
    'langdetect~=1.0,>=1.0.7',
    'librabbitmq~=1.0,>=1.6.1',
    'nameparser~=0.0,>=0.5.3',
    'orcid~=0.0,>=0.7.0',
    'plotextractor~=0.0,>=0.1.6',
    'python-redis-lock~=3.0,>=3.2.0',
    'raven~=5.0,>=5.1.0,<5.1.1',
    'refextract~=0.0,>=0.2.2',
    'requests~=2.0,>=2.18.4',
    'setproctitle~=1.0,>=1.1.10',
    'timeout-decorator~=0.0,>=0.4.0',
    'workflow~=2.0,>=2.1.3',
]

tests_require = [
    'flake8-future-import~=0.0,>=0.4.3',
    'mock~=2.0,>=2.0.0',
    'pytest-cov~=2.0,>=2.5.1',
    'pytest-flake8~=0.0,>=0.8.1',
    'pytest-selenium~=1.0,>=1.11.1',
    'pytest~=3.0,>=3.2.2',
    'requests_mock~=1.0,>=1.3.0',
]

extras_require = {
    'docs': [
        'Sphinx~=1.0,<1.6',
    ],
    'build-node': [
        'ipdb',
    ],
    'web-node': [
        'gunicorn',
    ],
    'worker-node': [
        'superlance',
        'flower',
    ],
    'crawler-node': [
        'hepcrawl~=2.0,>=2.0.1',
    ],
    'tests': tests_require,
    'xrootd': [
        'invenio-xrootd~=1.0,>=1.0.0a5',
        'xrootdpyfs~=0.0,>=0.1.5',
    ],
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('xrootd',):
        continue
    extras_require['all'].extend(reqs)

setup_requires = []

packages = find_packages(exclude=['docs'])

# Load __version__, should not be done using import.
# http://python-packaging-user-guide.readthedocs.org/en/latest/tutorial.html
g = {}
with open(os.path.join('inspirehep', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']


setup(
    name='Inspirehep',
    version=version,
    url='https://github.com/inspirehep/inspire-next',
    license='GPLv2',
    author='CERN',
    author_email='admin@inspirehep.net',
    description=__doc__,
    long_description=readme,
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    setup_requires=setup_requires,
    extras_require=extras_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
    ],
    entry_points={
        'console_scripts': [
            'inspirehep = inspirehep.cli:cli',
        ],
        'invenio_access.actions': [
            'view_restricted_collection'
            ' = inspirehep.modules.records.permissions:'
            'action_view_restricted_collection',
            'update_collection'
            ' = inspirehep.modules.records.permissions:'
            'action_update_collection',
            'admin_holdingpen_authors = inspirehep.modules.authors.permissions:action_admin_holdingpen_authors'
        ],
        'invenio_base.api_apps': [
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_search = inspirehep.modules.search:InspireSearch',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
            'invenio_collections = invenio_collections:InvenioCollections',
        ],
        'invenio_base.apps': [
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_fixtures = inspirehep.modules.fixtures:InspireFixtures',
            'inspire_theme = inspirehep.modules.theme:INSPIRETheme',
            'inspire_migrator = inspirehep.modules.migrator:InspireMigrator',
            'inspire_search = inspirehep.modules.search:InspireSearch',
            'inspire_authors = inspirehep.modules.authors:InspireAuthors',
            'inspire_literaturesuggest = inspirehep.modules.literaturesuggest:InspireLiteratureSuggest',
            'inspire_forms = inspirehep.modules.forms:InspireForms',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
            'inspire_arxiv = inspirehep.modules.arxiv:InspireArXiv',
            'inspire_crossref = inspirehep.modules.crossref:InspireCrossref',
            'inspire_tools = inspirehep.modules.tools:InspireTools',
            'inspire_hal = inspirehep.modules.hal:InspireHAL',
        ],
        'invenio_assets.bundles': [
            'inspirehep_theme_css = inspirehep.modules.theme.bundles:css',
            'inspirehep_theme_js = inspirehep.modules.theme.bundles:js',
            'almondjs = inspirehep.modules.theme.bundles:almondjs',
            'requirejs = inspirehep.modules.theme.bundles:requirejs',
            'inspirehep_landing_page_css = inspirehep.modules.theme.bundles:landing_page_css',
            'inspirehep_author_profile_js = inspirehep.modules.authors.bundles:js',
            'inspirehep_author_update_css = inspirehep.modules.authors.bundles:update_css',
            'inspirehep_forms_css = inspirehep.modules.forms.bundles:css',
            'inspirehep_forms_js = inspirehep.modules.forms.bundles:js',
            'inspirehep_authors_update_form_js=inspirehep.modules.authors.bundles:updatejs',
            'inspirehep_detailed_js = inspirehep.modules.theme.bundles:detailedjs',
            'inspirehep_literaturesuggest_js = inspirehep.modules.literaturesuggest.bundles:js',
            'invenio_search_ui_search_js = inspirehep.modules.search.bundles:js',
            'inspirehep_holding_css = inspirehep.modules.theme.bundles:holding_pen_css',
            'inspirehep_holding_js = inspirehep.modules.workflows.bundles:details_js',
            'inspirehep_tools_authorlist_js = inspirehep.modules.tools.bundles:js'
        ],
        'invenio_base.api_blueprints': [
            'inspirehep_editor = inspirehep.modules.editor:blueprint'
        ],
        'invenio_jsonschemas.schemas': [
            'inspire_records = inspire_schemas',
        ],
        'invenio_search.mappings': [
            'records = inspirehep.modules.records.mappings',
            'holdingpen = inspirehep.modules.workflows.mappings',
        ],
        'invenio_workflows.workflows': [
            'author = inspirehep.modules.workflows.workflows:Author',
            'article = inspirehep.modules.workflows.workflows:Article',
        ],
        'invenio_pidstore.fetchers': [
            'inspire_recid_fetcher = inspirehep.modules.pidstore.fetchers:inspire_recid_fetcher',
        ],
        'invenio_pidstore.minters': [
            'inspire_recid_minter = inspirehep.modules.pidstore.minters:inspire_recid_minter',
        ],
        'invenio_workflows_ui.actions': [
            'author_approval = inspirehep.modules.workflows.actions.author_approval:AuthorApproval',
            'merge_approval = inspirehep.modules.workflows.actions.merge_approval:MergeApproval',
            'hep_approval = inspirehep.modules.workflows.actions.hep_approval:HEPApproval',
        ],
        'invenio_db.models': [
            'inspire_workflows_audit = inspirehep.modules.workflows.models',
        ],
        'invenio_celery.tasks': [
            'inspire_migrator = inspirehep.modules.migrator.tasks',
            'inspire_records = inspirehep.modules.records.tasks',
            'inspire_refextract = inspirehep.modules.refextract.tasks',
        ],
    },
    tests_require=tests_require,
)
