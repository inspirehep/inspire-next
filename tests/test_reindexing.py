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

"""Tests reindexing."""

import json

from invenio.testsuite import InvenioTestCase


class ReindexingTests(InvenioTestCase):
    def setUp(self):
        from invenio_ext.es import es
        from invenio_search.registry import mappings
        self.name = 'hep'
        self.mapping_filename = self.name + ".json"
        self.mapping = json.load(open(mappings[self.mapping_filename], "r"))
        self.current_index = es.indices.get_alias(self.name).keys()[0]
        self.future_index = self.name + '_v2' if self.current_index.endswith('_v1') else self.name + '_v1'
        self.current_count = es.count(self.current_index)['count']

    def test_reindexing(self):
        """Test simple reindexing of HEP"""
        from invenio_ext.es import es
        from inspirehep.manage import recreate_index
        # NOTE: currently, on Travis we have to disable the read_only functionality
        # since it seems to not work properly in that context.
        self.assert_(recreate_index(self.name, self.mapping, rebuild=True, delete_old=True))
        self.assertEqual(es.indices.get_alias(self.name).keys()[0], self.future_index)
        self.assertEqual(es.count(self.future_index)['count'], self.current_count)
