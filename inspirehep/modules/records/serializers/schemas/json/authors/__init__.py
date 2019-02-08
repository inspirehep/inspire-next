# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from inspire_dojson.utils import strip_empty_values

from marshmallow import Schema, fields, post_dump

from inspirehep.modules.records.serializers.schemas.base import JSONSchemaUIV1
from inspirehep.modules.records.utils import get_author_with_record_facet_author_name

from .common import PositionSchemaV1


class AuthorsMetadataSchemaV1(Schema):
    _collections = fields.Raw()
    acquisition_source = fields.Raw()
    advisors = fields.Raw()
    arxiv_categories = fields.Raw()
    awards = fields.Raw()
    birth_date = fields.Raw()
    control_number = fields.Raw()
    death_date = fields.Raw()
    deleted = fields.Raw()
    email_addresses = fields.Raw()
    ids = fields.Raw()
    inspire_categories = fields.Raw()
    name = fields.Raw()
    new_record = fields.Raw()
    positions = fields.Nested(PositionSchemaV1, dump_only=True, many=True)
    should_display_positions = fields.Method('get_should_display_positions')
    project_membership = fields.Raw()
    status = fields.Raw()
    stub = fields.Raw()
    urls = fields.Raw()
    facet_author_name = fields.Method('get_facet_author_name')

    @staticmethod
    def get_facet_author_name(data):
        if 'facet_author_name' not in data:
            return get_author_with_record_facet_author_name(data)
        else:
            return data['facet_author_name']

    @staticmethod
    def get_should_display_positions(data):
        positions = data.get('positions')

        if positions is None:
            return False

        if len(positions) == 1:
            position = positions[0]

            return position.get('current') is not True or \
                any(key in position for key in ['rank', 'start_date', 'end_date'])

        return True

    @post_dump
    def strip_empty(self, data):
        return strip_empty_values(data)


class AuthorsRecordSchemaJSONUIV1(JSONSchemaUIV1):
    metadata = fields.Nested(AuthorsMetadataSchemaV1, dump_only=True)
