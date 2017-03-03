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
import pytest

from inspirehep.modules.converter import convert


@pytest.fixture
def oai_xml():
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv.xml'
        )
    )


@pytest.fixture
def oai_xml_result():
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'arxiv_marcxml.xml'
        )
    )


def test_xslt(oai_xml, oai_xml_result):
    """Test conversion of XSLT from XML."""
    xml = convert(xml=oai_xml, xslt_filename="oaiarXiv2marcxml.xsl")
    assert xml
    assert xml == oai_xml_result
