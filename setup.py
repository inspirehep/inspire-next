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
import re
import glob

from setuptools import setup, find_packages


def read_requirements(filename='requirements.txt'):
    req = []
    dep = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            if '://' in line:
                dep.append(str(line[:-1]))
            else:
                req.append(str(line))
    return req, dep

install_requires, dependency_links = read_requirements()

packages = find_packages(exclude=['docs'])

setup(
    name='Inspire',
    version='dev',
    url='https://github.com/inspirehep/inspire-next',
    license='GPLv3',
    author='CERN',
    author_email='admin@inspirehep.net',
    description='Digital library software',
    long_description=__doc__,
    packages=packages,
    namespace_packages=["inspire", "inspire.ext", ],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    dependency_links=dependency_links,
    test_suite='inspire.testsuite.suite',
    entry_points={
        'invenio.config': [
            "inspire = inspire.config"
        ]
    },
)
