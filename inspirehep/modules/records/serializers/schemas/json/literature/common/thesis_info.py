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

from marshmallow import Schema, fields, missing

from inspire_utils.date import format_date


class ThesisInfoSchemaV1(Schema):
    institutions = fields.Raw()
    defense_date = fields.Method('get_formatted_defense_date')
    date = fields.Method('get_formatted_date')
    degree_type = fields.Method('get_formatted_degree_type')

    def get_formatted_degree_type(self, info):
        degree_type = info.get('degree_type')
        if degree_type is None:
            return missing
        elif degree_type == 'phd':
            return 'PhD'
        return degree_type.title()

    def get_formatted_date(self, info):
        date = info.get('date')
        if date is None:
            return missing
        return format_date(date)

    def get_formatted_defense_date(self, info):
        defense_date = info.get('defense_date')
        if defense_date is None:
            return missing
        return format_date(defense_date)
