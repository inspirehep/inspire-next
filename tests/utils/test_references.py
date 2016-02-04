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

"""Unit tests for the function rendering references."""

from invenio_base.wrappers import lazy_import

from invenio_testing import InvenioTestCase

import mock


Record = lazy_import('invenio_records.api.Record')


class ReferencesTests(InvenioTestCase):

    """Unit tests for the function rendering references."""

    def test_references_no_references(self):
        from inspirehep.utils.references import render_references

        no_references = Record({})

        expected = []
        result = render_references(no_references)

        self.assertEqual(expected, result)
