# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""Tests for Holdingpen templates."""

from __future__ import print_function, absolute_import

from bs4 import BeautifulSoup

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class HoldingPenTests(InvenioTestCase):

    """Test the templates."""

    def test_classification_ordered_keywords(self):
        """Test that classification results are ordered correctly."""
        from flask import render_template
        sample_result = {
            'name': 'classification',
            'result': {'dict': {'categories': {'Born-Infeld model': 'HEP',
                                               'Yang-Mills': 'HEP',
                                               'gauge field theory': 'HEP',
                                               'membrane model': 'HEP'},
                                'complete_output': {'Core keywords': {'Born-Infeld model': 4,
                                                                      'Yang-Mills': 2,
                                                                      'gauge field theory': 5,
                                                                      'membrane model': 46},
                                                    'Filtered Core keywords': {'Born-Infeld model': 4,
                                                                               'Yang-Mills': 2,
                                                                               'gauge field theory': 5,
                                                                               'membrane model': 46}}},
                       'fast_mode': False},
            'template': 'workflows/results/classifier.html'
        }
        output = render_template(
            sample_result.get("template"),
            results=sample_result
        )
        beauty = BeautifulSoup(output)

        expected_output = [
            u'membrane model (46)',
            u'gauge field theory (5)',
            u'Born-Infeld model (4)',
            u'Yang-Mills (2)',
            u'membrane model (46)',
            u'gauge field theory (5)',
            u'Born-Infeld model (4)',
            u'Yang-Mills (2)'
        ]
        result = [b.text for b in beauty.find_all("li")]
        self.assertEqual(result, expected_output)


TEST_SUITE = make_test_suite(HoldingPenTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
