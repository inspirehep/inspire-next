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

"""The next version of INSPIRE.
If you are updating this file (eg. adding entry points) don't forget to update
pyproject.toml which is used for local development. The guide how to do it might
be found here: https://docs.python.org/3/distutils/setupscript.html
"""

from __future__ import absolute_import, division, print_function

import os

from setuptools import setup


URL = 'https://github.com/inspirehep/inspire-next'

g = {}
with open(os.path.join('inspirehep', 'version.py'), 'rt') as f:
    exec(f.read(), g)
    version = g['__version__']

readme = open('README.rst').read()

setup_requires = []

install_requires = []

docs_require = []

tests_require = []

packages = []

extras_require = {}

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
            'migrator-use-api = inspirehep.modules.migrator.permissions:action_migrator_use_api',
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
            'inspire_records = inspirehep.modules.records.ext:InspireRecords',
            'inspire_search = inspirehep.modules.search:InspireSearch',
            'inspire_accounts = inspirehep.modules.accounts:InspireAccounts',
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_workflows = inspirehep.modules.workflows:InspireWorkflows',
        ],
        'invenio_base.api_blueprints': [
            'inspirehep_editor = inspirehep.modules.editor:blueprint_api',
            'inspirehep_records = inspirehep.modules.records.views:blueprint',
            'inspire_migrator = inspirehep.modules.migrator.views:blueprint',
            'inspire_submissions = inspirehep.modules.submissions.views:blueprint',
        ],
        'invenio_base.apps': [
            'inspire_arxiv = inspirehep.modules.arxiv:InspireArXiv',
            'inspire_authors = inspirehep.modules.authors:InspireAuthors',
            'inspire_crossref = inspirehep.modules.crossref:InspireCrossref',
            'inspire_fixtures = inspirehep.modules.fixtures:InspireFixtures',
            'inspire_forms = inspirehep.modules.forms:InspireForms',
            'inspirehep_logger = inspirehep.modules.logger:InspireLogger',
            'inspire_literaturesuggest = inspirehep.modules.literaturesuggest:InspireLiteratureSuggest',
            'inspire_migrator = inspirehep.modules.migrator:InspireMigrator',
            'inspire_orcid = inspirehep.modules.orcid:InspireOrcid',
            'inspire_records = inspirehep.modules.records.ext:InspireRecords',
            'inspire_search = inspirehep.modules.search:InspireSearch',
            'inspire_theme = inspirehep.modules.theme:INSPIRETheme',
            'inspire_tools = inspirehep.modules.tools:InspireTools',
            'inspire_utils = inspirehep.utils.ext:INSPIREUtils',
            'inspire_workflows = inspirehep.modules.workflows:InspireWorkflows',
        ],
        'invenio_base.blueprints': [
            'inspirehep_editor = inspirehep.modules.editor:blueprint',
        ],
        'invenio_config.module': [
            'inspirehep = inspirehep.config',
            'inspirehep_logger = inspirehep.modules.logger.config',
            'inspire_workflows = inspirehep.modules.workflows.config'
        ],
        'invenio_celery.tasks': [
            'inspire_migrator = inspirehep.modules.migrator.tasks',
            'inspire_orcid = inspirehep.modules.orcid.tasks',
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
        ],
        'invenio_workflows.workflows': [
            'article = inspirehep.modules.workflows.workflows:Article',
            'author = inspirehep.modules.workflows.workflows:Author',
            'manual_merge = inspirehep.modules.workflows.workflows:ManualMerge',
            'edit_article = inspirehep.modules.workflows.workflows:EditArticle',
            'core_selection = inspirehep.modules.workflows.workflows:CoreSelection'
        ],
        'invenio_workflows_ui.actions': [
            'author_approval = inspirehep.modules.workflows.actions.author_approval:AuthorApproval',
            'hep_approval = inspirehep.modules.workflows.actions.hep_approval:HEPApproval',
            'core_selection_approval = inspirehep.modules.workflows.actions.core_selection_approval:CoreSelectionApproval',
            'merge_approval = inspirehep.modules.workflows.actions.merge_approval:MergeApproval',
            'match_approval = inspirehep.modules.workflows.actions.match_approval:MatchApproval',
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
