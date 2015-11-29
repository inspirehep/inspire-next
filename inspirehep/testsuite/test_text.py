# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for text utls."""

from __future__ import print_function, absolute_import

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class TextTests(InvenioTestCase):

    """Test the text functions."""

    def setUp(self):
        self.bad_xml = (
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

        self.good_xml = (
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

        self.unicode_xml = "<record>Über</record>"
        self.good_unicode_xml = u'<?xml version="1.0" encoding="utf-8"?>\n<record>\xdcber</record>'

    def test_clean_xml(self):
        """Test proper handling when bad MARCXML is sent."""
        from inspirehep.utils.text import clean_xml

        self.assertEqual(clean_xml(self.bad_xml), self.good_xml)

    def test_unicode_clean_xml(self):
        """Test proper handling when bad MARCXML is sent."""
        from inspirehep.utils.text import clean_xml

        self.assertEqual(clean_xml(self.unicode_xml), self.good_unicode_xml)


TEST_SUITE = make_test_suite(TextTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
