# -*- coding: utf-8 -*-
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

import unittest
from invenio.testsuite import iter_suites


def suite():
    """Create the testsuite that has all the tests."""
    packages = [
        'inspire.modules.deposit',
        # Run after records have been created by other tests
        'inspire',
        'inspire.base',
    ]
    suite = unittest.TestSuite()
    for other_suite in iter_suites(packages=packages):
        suite.addTest(other_suite)
    return suite
