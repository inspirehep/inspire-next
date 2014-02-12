## This file is part of Invenio.
## Copyright (C) 2013, 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
INSPIRE overlay
----------------

INSPIRE overlay repository for Invenio.
"""
from __future__ import print_function

import re
import glob

from setuptools import setup, find_packages


def match_feature_name(filename):
    return re.match(r".*requirements-(\w+).txt$", filename).group(1)


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

# Finds all `requirements-*.txt` files and prepares dictionary with extra
# requirements (NOTE: no links are allowed here!)
extras_require = dict(map(
    lambda filename: (match_feature_name(filename),
                      read_requirements(filename)[0]),
    glob.glob('requirements-*.txt')))

packages = find_packages(exclude=['docs'])

setup(
    name='Inspire',
    version='1.9999-dev',
    url='https://github.com/inspirehep/inspire-next',
    license='GPLv2',
    author='CERN',
    author_email='admin@inspirehep.net',
    description='Digital library software',
    long_description=__doc__,
    packages=packages,
    package_dir={'invenio_docs': 'docs'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    dependency_links=dependency_links,
    extras_require=extras_require,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite='inspire.testsuite.suite',
    entry_points={
        'invenio.config': [
            "site = inspire.config"
        ]
    },
)
