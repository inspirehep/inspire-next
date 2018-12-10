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


class PositionSchemaV1(Schema):
    current = fields.Raw()
    institution = fields.Raw()
    rank = fields.Raw()
    display_date = fields.Method('get_display_date', default=missing)

    def get_display_date(self, data):
        current = data.get('current')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        suffixed_start_date = '{}-'.format(start_date) if start_date else ''

        if current:
            return '{}present'.format(suffixed_start_date)

        if end_date:
            return '{}{}'.format(suffixed_start_date, end_date)

        if start_date:
            return start_date

        return missing
