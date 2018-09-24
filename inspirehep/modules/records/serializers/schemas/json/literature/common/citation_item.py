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

from marshmallow import Schema, fields, post_dump

from inspire_dojson.utils import strip_empty_values

from inspirehep.modules.records.serializers.fields import ListWithLimit, NestedWithoutEmptyObjects

from .author import AuthorSchemaV1
from .publication_info_item import PublicationInfoItemSchemaV1


class CitationItemSchemaV1(Schema):
    authors = ListWithLimit(
        NestedWithoutEmptyObjects(AuthorSchemaV1, dump_only=True), limit=10)
    control_number = fields.Raw()
    publication_info = fields.List(
        NestedWithoutEmptyObjects(PublicationInfoItemSchemaV1, dump_only=True))
    titles = fields.Raw()
    earliest_date = fields.Raw()

    @post_dump
    def strip_empty(self, data):
        return strip_empty_values(data)
