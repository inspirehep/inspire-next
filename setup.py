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

"""INSPIRE overlay repository for Invenio."""

from __future__ import absolute_import, division, print_function

import os

from setuptools import find_packages, setup


readme = open('README.rst').read()

install_requires = [
    'amqp>=1.4.9,<2.0',
    'beard>=0.2.0,~=0.2',
    'celery<4.0',
    'Flask-Gravatar>=0.4.2',
    'plotextractor>=0.1.2',
    'refextract>=0.2.0',
    'orcid',
    'raven<=5.1.0',
    'flower',
    'langdetect>=1.0.6',
    'librabbitmq>=1.6.1',
    'idutils>=0.2.1',
    'invenio-access>=1.0.0a7',
    'invenio-accounts>=1.0.0b7',
    'invenio-admin>=1.0.0a3',
    'invenio-assets>=1.0.0b2',
    'invenio-base>=1.0.0a11',
    'invenio-cache>=1.0.0b1',
    'invenio-celery>=1.0.0a4',
    'invenio-classifier>=1.3.0',
    'invenio-collections>=1.0.0a3',
    'invenio-config>=1.0.0a1',
    'invenio-i18n>=1.0.0a4',
    'invenio-indexer>=1.0.0a10',
    'invenio-jsonschemas>=1.0.0a4',
    'invenio-logging>=1.0.0b3',
    'invenio-mail>=1.0.0a4',
    'invenio-oauthclient>=1.0.0b1',
    'invenio-orcid>=1.0.0a1',
    'invenio-records>=1.0.0a16',  # Add [versioning] in the future
    'invenio-rest[cors]>=1.0.0a7',
    'invenio-search>=1.0.0a7',
    'invenio-records-rest>=1.0.0a17',
    'invenio-records-ui>=1.0.0a6',
    'invenio-files-rest>=1.0.0a3',
    'invenio-records-files>=1.0.0a5',
    'invenio-userprofiles>=1.0.0a7',
    'invenio-oaiharvester==1.0.0a2',
    'invenio>=3.0.0a1,<3.1.0',
    'inspire-crawler~=0.0,>=0.2.7',
    'inspire-dojson~=48.0,>=48.0.0',
    'inspire-schemas~=48.0,>=48.0.0',
    'inspire-utils~=0.0,>=0.0.6',
    'Flask>=0.11.1',
    'Flask-Breadcrumbs>=0.3.0',
    'flask-shell-ipython>=0.2.2',
    'workflow~=2.0,>=2.0.1',
    'SQLAlchemy>=1.0.14,<1.1',
    'nameparser>=0.4.0',
    'iso8601>=0.1.11',
    'invenio-trends>=1.0.0a1',
    'invenio-trends-ui>=1.0.0a1',
    'elasticsearch<3.0.0',
    'Flask-Login~=0.0,>=0.4.0',
    'invenio-workflows~=6.0,>=6.0.5',
    'invenio-workflows-files~=0.0,>=0.0.4',
    'invenio-workflows-ui~=1.0,>=1.0.31',
    'elasticsearch-dsl<2.2.0',
    'pycountry>=17.1.8',
    'Flask_CeleryExt>=0.3.0',
    'python-redis-lock~=3.2',
    'backoff~=1.0,>=1.4.2',
    'requests~=2.0,>=2.15.1',
    'timeout-decorator~=0.0,>=0.3.3',
    'Babel~=2.0,>=2.4.0',
    'setproctitle~=1.0,>=1.1.10',
    'backports.tempfile>=1.0rc1',
    'simplekv~=0.0,<0.11',
    'node-semver~=0.0,<0.2',
]

tests_require = [
    'flake8-future-import>=0.4.3',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-flake8>=0.8.1',
    'pytest-selenium>=1.3.1',
    'pytest>=2.8.0',
    'mock>=1.3.0',
    'requests_mock',
]

extras_require = {
    'docs': [
        'Sphinx~=1.0,<1.6',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.0b2',
    ],
    'web-node': [
        'gunicorn',
    ],
    'crawler': [
        'hepcrawl~=0.0,>=0.3.4',
    ],
    'tests': tests_require,
    'xrootd': [
        'invenio-xrootd~=1.0,>=1.0.0a5',
        'xrootdpyfs~=0.0,>=0.1.5',
    ],
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('postgresql', 'xrootd'):
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
            'admin_holdingpen_authors = inspirehep.modules.authors.permissions:action_admin_holdingpen_authors',
            'editor_manage_tickets = inspirehep.modules.editor.permissions:action_editor_manage_tickets'
        ],
        'invenio_base.api_apps': [
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_search = inspirehep.modules.search:INSPIRESearch',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
            'invenio_collections = invenio_collections:InvenioCollections',
        ],
        'invenio_base.apps': [
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_fixtures = inspirehep.modules.fixtures:INSPIREFixtures',
            'inspire_theme = inspirehep.modules.theme:INSPIRETheme',
            'inspire_migrator = inspirehep.modules.migrator:InspireMigrator',
            'inspire_search = inspirehep.modules.search:INSPIRESearch',
            'inspire_authors = inspirehep.modules.authors:INSPIREAuthors',
            'inspire_literature_suggest = inspirehep.modules.literaturesuggest:INSPIRELiteratureSuggestion',
            'inspire_forms = inspirehep.modules.forms:INSPIREForms',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
            'inspire_arxiv = inspirehep.modules.arxiv:InspireArXiv',
            'inspire_crossref = inspirehep.modules.crossref:InspireCrossref',
            'inspire_orcid = inspirehep.modules.orcid:INSPIREOrcid',
            'inspire_disambiguation = inspirehep.modules.disambiguation:InspireDisambiguation',
            'inspire_tools = inspirehep.modules.tools:INSPIRETools',
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
            'inspire_disambiguation = inspirehep.modules.disambiguation.models',
        ],
        'invenio_celery.tasks': [
            'inspire_disambiguation = inspirehep.modules.disambiguation.tasks',
            'inspire_migrator = inspirehep.modules.migrator.tasks',
            'inspire_records = inspirehep.modules.records.tasks',
            'inspire_refextract = inspirehep.modules.refextract.tasks',
        ],
    },
    tests_require=tests_require,
)
