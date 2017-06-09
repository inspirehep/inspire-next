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
    'amqp>=1.4.9,~=1.4',
    'celery>=3.1.25,~=3.1',
    'Flask-Gravatar>=0.4.2,~=0.4',
    'HarvestingKit>=0.6.9,~=0.6',
    'plotextractor>=0.1.6,~=0.1',
    'refextract>=0.1.0,~=0.1',
    'Sickle>=0.6.1,~=0.6',
    'orcid>=0.7.0,~=0.7',
    'raven>=5.1.0,~=5.1',
    'retrying>=1.3.3,~=1.3',
    'flower>=0.9.1,~=0.9',
    'rt>=1.0.9,~=1.0',
    'langdetect>=1.0.7,~=1.0',
    'librabbitmq>=1.6.1,~=1.6',
    'invenio-access>=1.0.0a12,~=1.0',
    'invenio-accounts>=1.0.0b4,~=1.0',
    'invenio-admin>=1.0.0b1,~=1.0',
    'invenio-assets>=1.0.0b6,~=1.0',
    'invenio-base>=1.0.0a14,~=1.0',
    'invenio-celery>=1.0.0b2,~=1.0',
    'invenio-classifier>=1.1.2,~=1.1',
    'invenio-collections>=1.0.0a3,~=1.0',
    'invenio-config>=1.0.0b3,~=1.0',
    'invenio-i18n>=1.0.0b3,~=1.0',
    'invenio-indexer>=1.0.0a9,~=1.0',
    'invenio-jsonschemas>=1.0.0a4,~=1.0',
    'invenio-logging>=1.0.0b1,~=1.0',
    'invenio-mail>=1.0.0b1,~=1.0',
    'invenio-oauthclient>=1.0.0a13,~=1.0',
    'invenio-orcid>=1.0.0a1,~=1.0',
    'invenio-records>=1.0.0b1,~=1.0',  # Add [versioning] in the future
    'invenio-rest>=1.0.0a10,~=1.0',
    'invenio-search>=1.0.0a9,~=1.0',
    'invenio-records-rest>=1.0.0a18,~=1.0',
    'invenio-records-ui>=1.0.0a9,~=1.0',
    'invenio-files-rest>=1.0.0a16,~=1.0',
    'invenio-records-files>=1.0.0a9,~=1.0',
    'invenio-userprofiles>=1.0.0a10,~=1.0',
    'invenio-oaiharvester>=1.0.0a2,~=1.0',
    'invenio-utils>=0.2.0,~=0.2',  # Not fully Invenio 3 ready
    'invenio>=3.0.0a4,~=3.0',
    'inspire-crawler>=0.2.11,~=0.2',
    'inspire-schemas>=31.1.0,~=31.1',
    'dojson>=1.3.1,~=1.3',
    'Flask>=0.12.2,~=0.12',
    'Flask-Breadcrumbs>=0.4.0,~=0.4',
    'Flask-Caching>=1.2.0,~=1.2',
    'Flask-Script>=2.0.5,~=2.0',
    'flask-shell-ipython>=0.2.2,~=0.2',
    'fs>=0.5.5a1,~=0.5', # TODO: remove once invenio-files-rest#130 is fixed
    'jsmin>=2.2.2,~=2.2',
    'pytest-runner>=2.11.1,~=2.11',
    # FIXME: Commented for testing, to use a custom fork
    #'workflow>=2.0.0',
    'SQLAlchemy>=1.0.17,~=1.0',
    'nameparser>=0.5.2,~=0.5',
    'iso8601>=0.1.11,~=0.1',
    'invenio-trends>=1.0.0a1,~=1.0',
    'invenio-trends-ui>=1.0.0a1,~=1.0',
    'elasticsearch>=2.4.1,~=2.4',
    'Flask-Login>=0.3.2,~=0.3',
    'invenio-workflows>=6.0.6,~=6.0',
    'invenio-workflows-files>=0.0.6,~=0.0',
    'invenio-workflows-ui>=1.0.32,~=1.0',
    'elasticsearch-dsl>=2.1.0,~=2.1',
    'pycountry>=17.5.14,~=17.5',
    'python-redis-lock>=3.2.0,~=3.2',
    'backoff>=1.4.3,~=1.4',
    'requests>=2.15.1,~=2.15',
]

tests_require = [
    'check-manifest>=0.35,~=0',
    'coverage>=4.4.1,~=4.4',
    'flake8-future-import>=0.4.3,~=0.4',
    'isort>=4.2.15,~=4.2',
    'pep257>=0.7.0,~=0.7',
    'pytest-cache>=1.0,~=1',
    'pytest-cov>=2.5.1,~=2.5',
    'pytest-flake8>=0.8.1,~=0.8',
    'pytest-httpretty>=0.2.0,~=0.2',
    'pytest-selenium>=1.10.0,~=1.10',
    'pytest>=3.1.1,~=3.1',
    'mock>=2.0.0,~=2.0',
    'requests_mock>=1.3.0,~=1.3',
]

extras_require = {
    'docs': [
        'six>=1.10.0,~=1.10',
        'mock>=2.0.0,~=2.0',
        'Sphinx>=1.5.6,~=1.5',
        'sphinxcontrib-napoleon>=0.6.1,~=0.6',
        'docutils>=0.13.1,~=0.13',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.0b7,~=1.0',
    ],
    'mysql': [
        'invenio-db[mysql,versioning]>=1.0.0b7,~=1.0',
    ],
    'sqlite': [
        'invenio-db[versioning]>=1.0.0b7,~=1.0',
    ],
    'web-node': [
        'gunicorn>=19.7.1,~=19.7',
    ],
    'crawler': [
        'hepcrawl>=0.3.21,~=0.3',
    ],
    'tests': tests_require,
    'development': [
        'Flask-DebugToolbar>=0.9',
        'ipython',
        'ipdb',
        'kwalitee',
        'honcho',
        'gunicorn',
    ]
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('postgresql', 'mysql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=2.4.0,~=2.4',
]

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
        'dojson.cli.rule': [
            'hep = inspirehep.dojson.hep:hep',
            'hep2marc = inspirehep.dojson.hep:hep2marc',
            'hepnames = inspirehep.dojson.hepnames:hepnames',
            'hepnames2marc = inspirehep.dojson.hepnames2marc:hepnames2marc',
        ],
        'invenio_access.actions': [
            'view_restricted_collection'
            ' = inspirehep.modules.records.permissions:'
            'action_view_restricted_collection',
            'admin_holdingpen_authors = inspirehep.modules.authors.permissions:action_admin_holdingpen_authors'
        ],
        'invenio_base.api_apps': [
            'inspire_cache = inspirehep.modules.cache.ext:INSPIRECache',
            'inspire_search = inspirehep.modules.search:INSPIRESearch',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
            'invenio_collections = invenio_collections:InvenioCollections',
        ],
        'invenio_base.apps': [
            'inspire_cache = inspirehep.modules.cache.ext:INSPIRECache',
            'inspire_fixtures = inspirehep.modules.fixtures:INSPIREFixtures',
            'inspire_theme = inspirehep.modules.theme:INSPIRETheme',
            'inspire_migrator = inspirehep.modules.migrator:INSPIREMigrator',
            'inspire_search = inspirehep.modules.search:INSPIRESearch',
            'inspire_authors = inspirehep.modules.authors:INSPIREAuthors',
            'inspire_literature_suggest = inspirehep.modules.literaturesuggest:INSPIRELiteratureSuggestion',
            'inspire_forms = inspirehep.modules.forms:INSPIREForms',
            'inspire_workflows = inspirehep.modules.workflows:INSPIREWorkflows',
            'arxiv = inspirehep.modules.arxiv:Arxiv',
            'crossref = inspirehep.modules.crossref:CrossRef',
            'inspire_orcid = inspirehep.modules.orcid:INSPIREOrcid',
            'inspire_disambiguation = inspirehep.modules.disambiguation:InspireDisambiguation',
            'inspire_tools = inspirehep.modules.tools:INSPIRETools',
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
    },
    tests_require=tests_require,
)
