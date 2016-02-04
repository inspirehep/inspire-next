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

"""Unit tests for the bibtex_booktitle helpers."""

from invenio_base.wrappers import lazy_import

from invenio_testing import InvenioTestCase


Record = lazy_import('invenio_records.api.Record')


class GenerateBooktitleTests(InvenioTestCase):

    """Unit tests for the bibtex_booktitle helpers."""

    def test_generate_booktitle_no_publication_info(self):
        from inspirehep.utils.bibtex_booktitle import generate_booktitle

        no_publication_info = Record({})

        expected = ''
        result = generate_booktitle(no_publication_info)

        self.assertEqual(expected, result)

    def test_traverse_yields_preorder(self):
        from inspirehep.utils.bibtex_booktitle import traverse

        tree = [[1, 2], [3, 4], [5, [6]]]

        expected = [1, 2, 3, 4, 5, 6]
        result = list(traverse(tree))

        self.assertEqual(expected, result)
