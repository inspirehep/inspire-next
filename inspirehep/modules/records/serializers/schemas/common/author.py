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

from marshmallow import Schema, fields, missing, pre_dump


class AuthorSchemaV1(Schema):
    affiliations = fields.Raw()
    alternative_names = fields.Raw()
    credit_roles = fields.Raw()
    curated_relation = fields.Raw()
    emails = fields.Raw()
    full_name = fields.Raw()
    ids = fields.Raw()
    inspire_roles = fields.Raw()
    raw_affilitaions = fields.Raw()
    record = fields.Raw()
    signature_block = fields.Raw()
    uuid = fields.Raw()
    first_name = fields.Method('get_first_name')
    last_name = fields.Method('get_last_name')

    def get_first_name(self, data):
        names = data.get('full_name', '').split(',', 1)

        if len(names) > 1:
            return names[1].replace(',', '').strip()

        return names[0]

    def get_last_name(self, data):
        names = data.get('full_name', '').split(',', 1)

        if len(names) > 1:
            return names[0]

        return missing

    @pre_dump
    def filter(self, data):
        if 'inspire_roles' in data:
            if 'supervisor' in data.get('inspire_roles', ['author']):
                return {}
        return data
