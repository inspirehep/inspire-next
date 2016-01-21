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

from invenio_testing import InvenioTestCase

from inspirehep.modules.authors.receivers import assign_signature_block


class AuthorBlockTests(InvenioTestCase):

    def test_assign_signature_block_empty(self):
        """Test that assign_signature_block behaves on empty records."""
        sample_record = {}
        assign_signature_block(recid=1, json=sample_record)
        assert sample_record == {}

    def test_assign_signature_block_no_authors(self):
        """Test that assign_signature_block behaves on no authors."""
        sample_record = {
            "authors": {}
        }
        assign_signature_block(recid=1, json=sample_record)
        assert len(sample_record['authors']) == 0

    def test_assign_signature_block_addition(self):
        """Test that assign_signature_block adds signature_block."""
        sample_record = {
            "authors": [{
                "full_name": "John Ellis"
            }]
        }
        assign_signature_block(recid=1, json=sample_record)
        assert 'signature_block' in sample_record['authors'][0]

    def test_assign_signature_block_malformed(self):
        """Test that assign_signature_block adds signature_block."""
        sample_record = {
            "authors": [{
                "full_name": ", "
            }]
        }
        assign_signature_block(recid=1, json=sample_record)
        assert 'signature_block' not in sample_record['authors'][0]
