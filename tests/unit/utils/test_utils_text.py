# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tests for text utls."""

from __future__ import absolute_import, division, print_function

import pytest


@pytest.fixture
def bad_xml():
    return (
        '<record><datafield tag="245" ind1="" ind2="">'
        '<subfield code="a">\xc3\x81xions, m\xc3\xa1jorons e neutrinos'
        ' em extens\xc3\xb5es do modelo padr\xc3\xa3o</subfield></datafield>'
        '<datafield tag="520" ind1="" ind2=""><subfield code="a">'
        'based on the SU(3)L \xe2\x8a\x97 U(1)X and SU(2)L \xe2\x8a\x97 U(1)Y \x02 \xe2\x8a\x97 U(1)B\xe2\x88\x92L gauge symmetries.'
        'Secondly, an electroweak model based on the gauge symmetry '
        'SU(2)L \xe2\x8a\x97 U(1)Y \x02 \xe2\x8a\x97 U(1)B\xe2\x88\x92L which has right-handed '
        'Finally, a N = 1 supersymmetric extension of the a B \xe2\x88\x92 L model with three'
        '</subfield></datafield></record>'
    )


@pytest.fixture
def good_xml():
    return (
        u'<?xml version="1.0" encoding="utf-8"?>\n<record>'
        u'<datafield ind1="" ind2="" tag="245"><subfield code="a">'
        u'\xc1xions, m\xe1jorons e neutrinos em extens\xf5es do modelo'
        u' padr\xe3o</subfield></datafield><datafield ind1="" ind2="" tag="520">'
        u'<subfield code="a">based on the SU(3)L \u2297 U(1)X and SU(2)L'
        u' \u2297 U(1)Y  \u2297 U(1)B\u2212L gauge symmetries.Secondly, '
        u'an electroweak model based on the gauge symmetry SU(2)L'
        u' \u2297 U(1)Y  \u2297 U(1)B\u2212L which has right-handed '
        u'Finally, a N = 1 supersymmetric extension of the a B \u2212 L model'
        u' with three</subfield></datafield></record>'
    )


@pytest.fixture
def unicode_xml():
    return "<record>Über</record>"


@pytest.fixture
def good_unicode_xml():
    return u'<?xml version="1.0" encoding="utf-8"?>\n<record>\xdcber</record>'


def test_clean_xml(bad_xml, good_xml):
    """Test proper handling when bad MARCXML is sent."""
    from inspirehep.utils.text import clean_xml

    assert clean_xml(bad_xml) == good_xml


def test_unicode_clean_xml(unicode_xml, good_unicode_xml):
    """Test proper handling when bad MARCXML is sent."""
    from inspirehep.utils.text import clean_xml

    assert clean_xml(unicode_xml) == good_unicode_xml
