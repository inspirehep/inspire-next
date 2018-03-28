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

from __future__ import absolute_import, division, print_function

import os
import pkg_resources

from inspirehep.modules.migrator.tasks import read_file


def test_read_file_reads_xml_file_correctly():
    xml_file = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663924.xml'))

    with open(xml_file, 'rb') as f:
        expected = f.readlines()
    result = list(read_file(xml_file))

    assert expected == result


def test_read_file_reads_gzipped_file_correctly():
    xml_file = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663924.xml'))
    gzipped_file = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663924.xml.gz'))

    with open(xml_file, 'rb') as f:
        expected = f.readlines()
    result = list(read_file(gzipped_file))

    assert expected == result


def test_read_file_reads_prodsync_file_correctly():
    xml_files = [
        pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663923.xml')),
        pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663924.xml')),
    ]

    prodsync_file = pkg_resources.resource_filename(__name__, os.path.join('fixtures', 'micro-prodsync.tar'))

    expected = []
    for xml_file in xml_files:
        with open(xml_file, 'rb') as f:
            expected.extend(f.readlines())
    result = list(read_file(prodsync_file))

    assert expected == result
