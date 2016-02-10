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

"""Tests migration utils of records."""

from invenio.testsuite import InvenioTestCase


class SchemaMigratorUtilsTests(InvenioTestCase):

    def test_json_schema_loading(self):
        """Test that all JSON schemas load."""
        from inspirehep.modules.migrator.utils import load_schemas
        assert list(load_schemas())

    def test_json_schema_validation(self):
        """Test that all schema validation works."""
        from inspirehep.modules.migrator.utils import validate
        data = {
            '$schema': 'hep-0.0.1.json',
            'titles': [{
                'title': "Value"
            }]
        }
        assert validate(data) is None

    def test_json_schema_validation_error(self):
        """Test that all schema validation fails accordingly."""
        from inspirehep.modules.migrator.utils import validate
        from jsonschema import ValidationError
        data = {
            '$schema': 'hep-0.0.1.json',
            'titles': {
                'title': "Value"
            }
        }
        self.assertRaises(ValidationError, validate, data)
