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

"""Wrapper for an XSLT engine."""

from __future__ import absolute_import, division, print_function

import os
import lxml.etree as ET


def convert(xml, xslt_filename):
    """Convert XML using given XSLT stylesheet."""
    if not os.path.isabs(xslt_filename):
        prefix_dir = os.path.dirname(os.path.realpath(__file__))
        xslt_filename = os.path.join(prefix_dir, "stylesheets", xslt_filename)

    dom = ET.fromstring(xml)
    xslt = ET.parse(xslt_filename)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return ET.tostring(newdom, pretty_print=False)
