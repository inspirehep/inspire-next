# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

"""INSPIRE overlay repository for Invenio."""

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


requirements = [
    "rt",
    "HarvestingKit>=0.6.2",
    "mixer==4.9.5",  # FIXME: Due to incompatibility with our mixer usage
    "raven==5.0.0",  # FIXME: To be compatible with our sentry version
    "orcid",
    "retrying",
    "invenio-query-parser>=0.3.0",
    "invenio_classifier==0.1.0",
    "invenio-access==0.1.0",
    "invenio-accounts==0.1.2",
    "invenio-client==0.1.0",
    "invenio-deposit==0.2.0",
    "invenio-formatter==0.2.1",
    "invenio-groups==0.1.3",
    "invenio-knowledge==0.1.0",
    "invenio-oauth2server==0.1.1",
    "invenio-oauthclient==0.1.1",
    "invenio-pidstore[datacite]==0.1.1",
    "invenio-previewer==0.1.0",
    "invenio-records==0.3.2",
    "invenio-documents==0.1.0.post2",
    "invenio-unapi==0.1.0",
    "invenio-upgrader==0.1.0",
    "invenio-webhooks==0.1.0",
]

test_requirements = [
    'unittest2>=1.1.0',
    'Flask-Testing>=0.4.2',
    'pytest>=2.8.0',
    'pytest-cov>=2.1.0',
    'pytest-pep8>=1.0.6',
    'coverage>=4.0.0',
]


class PyTest(TestCommand):

    """PyTest Test."""

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        """Init pytest."""
        TestCommand.initialize_options(self)
        self.pytest_args = []
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        config = ConfigParser()
        config.read('pytest.ini')
        self.pytest_args = config.get('pytest', 'addopts').split(' ')

    def finalize_options(self):
        """Finalize pytest."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

packages = find_packages(exclude=['docs'])

# Load __version__, should not be done using import.
# http://python-packaging-user-guide.readthedocs.org/en/latest/tutorial.html
g = {}
with open(os.path.join('inspire', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']


setup(
    name='Inspire',
    version=version,
    url='https://github.com/inspirehep/inspire-next',
    license='GPLv2',
    author='CERN',
    author_email='admin@inspirehep.net',
    description=__doc__,
    long_description=open('README.rst', 'rt').read(),
    packages=packages,
    namespace_packages=["inspire", "inspire.ext", ],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    extras_require={
        'development': [
            'Flask-DebugToolbar>=0.9',
            'ipython',
            'ipdb',
            'kwalitee'
        ],
        'docs': [
            'Sphinx>=1.3',
            'sphinx_rtd_theme>=0.1.7'
        ],
        'tests': test_requirements
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points={
        'invenio.config': [
            "inspire = inspire.config"
        ]
    },
    test_suite='inspire.testsuite',
    tests_require=test_requirements,
    cmdclass={'test': PyTest}
)
