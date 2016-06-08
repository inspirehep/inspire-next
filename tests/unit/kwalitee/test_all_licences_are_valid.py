# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

from __future__ import absolute_import, division, print_function

import os
import pkg_resources
import re


PYTHON_LICENCE = re.compile(r'''# -\*- coding: utf-8 -\*-
#
# This file is part of INSPIRE.
# Copyright \(C\) \d{4}(, \d{4})* CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# \(at your option\) any later version.
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
# or submit itself to any jurisdiction.''', re.MULTILINE)


def read_file(path):
    return pkg_resources.resource_string('inspirehep', path)


def check_licence(path):
    if path.endswith('.py'):
        return PYTHON_LICENCE.match(read_file(path))

    return True


def test_all_licences_are_valid():
    failed = []

    for dir_, _, filenames in os.walk('inspirehep'):
        dir_path = os.path.sep.join(dir_.split(os.path.sep)[1:])
        for filename in filenames:
            filepath = os.path.join(dir_path, filename)
            if not check_licence(filepath):
                failed.append(filepath)

    assert failed == []
