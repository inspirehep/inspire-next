# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Unit tests for the function rendering citations."""

from invenio_base.wrappers import lazy_import

from invenio_testing import InvenioTestCase

import mock


Record = lazy_import('invenio_records.api.Record')


class CitationsTests(InvenioTestCase):

    """Unit tests for the function rendering citations."""

    @mock.patch('inspirehep.utils.citations.Results.records')
    def test_citations_no_citations(self, records):
        records.return_value = []

        from inspirehep.utils.citations import render_citations

        no_citations = Record({'control_number': 1})

        expected = []
        result = render_citations(no_citations)

        self.assertEqual(expected, result)

    @mock.patch('inspirehep.utils.citations.render_template_to_string')
    @mock.patch('inspirehep.utils.citations.Results.records')
    def test_citations_one_citation(self, records, rtts):
        records.return_value = [{'citation_count': 1}]
        rtts.return_value = 'record 1'

        from inspirehep.utils.citations import render_citations

        one_citation = Record({'control_number': 1})

        expected = [['record 1', 1]]
        result = render_citations(one_citation)

        self.assertEqual(expected, result)
