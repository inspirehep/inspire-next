# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""Vcr module configuration for Inspire"""

from __future__ import absolute_import, division, print_function

import logging
import vcr


def inspire_vcr(folder):
    logging.basicConfig()
    vcr_log = logging.getLogger("vcr")
    vcr_log.setLevel(logging.INFO)

    my_vcr = vcr.VCR(
        serializer='yaml',
        cassette_library_dir='inspirehep/testlib/cassettes/{}'.format(folder),
        record_mode='once',
        match_on=['method', 'host'],
    )
    return my_vcr
