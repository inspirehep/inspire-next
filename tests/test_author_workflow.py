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

"""Tests for the author form workflows."""

import os
import json
import pkg_resources

from invenio_testing import InvenioTestCase


class AuthorWorkflowTests(InvenioTestCase):

    """Tests for the author workflow."""

    def setup_class(self):
        """Sets up Mock object."""

        self.test_author_form_converted = json.loads(
            pkg_resources.resource_string(
                'tests',
                os.path.join(
                    'fixtures',
                    'test_author_form_converted.json'
                )
            )
        )

        class MockObj(object):
            def __init__(self):
                self._extra_data = {'formdata': {}}
                self._data = json.loads(
                    pkg_resources.resource_string(
                        'tests',
                        os.path.join(
                            'fixtures',
                            'test_author_form.json'
                        )
                    )
                )

            @property
            def extra_data(self):
                return self._extra_data

            @property
            def data(self):
                return self._data

            @property
            def id_user(self):
                return 1

            @property
            def id(self):
                return 99

            @property
            def model(self):
                return 'banana'

        class MockWorkflowDefinition(object):
            def model(self, obj):
                return obj.model

        class MockEng(object):
            @property
            def workflow_definition(self):
                return MockWorkflowDefinition()

        self.MockObj = MockObj
        self.MockEng = MockEng

    def test_form_dojson_data_model_conversion(self):
        """Test if the form data gets converted properly to dojson."""
        from inspirehep.modules.authors.tasks import convert_data_to_model

        obj = self.MockObj()
        eng = self.MockEng()

        f = convert_data_to_model()

        f(obj, eng)

        self.assertEqual(obj.data, self.test_author_form_converted)
