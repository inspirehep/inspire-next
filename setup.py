# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2012, 2013 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
INSPIRE overlay
----------------

INSPIRE overlay repository for Invenio.
"""

import os
from setuptools import setup, find_packages

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
    install_requires=[
        "rt",
        "HarvestingKit",
        "mixer",
        "ipython",
        "Babel>=1.3",
        "Invenio",
    ],
    dependency_links=[
        "git+https://github.com/inspirehep/invenio@labs#egg=Invenio"
    ],
    extras_require={
        'development': [
            'Flask-DebugToolbar>=0.9',
            'setuptools-bower>=0.2'
        ],
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
    tests_require=[
        'nose',
        'Flask-Testing'
    ]
)
