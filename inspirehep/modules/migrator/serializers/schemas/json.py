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

"""Marshmallow JSON error schema."""

from __future__ import absolute_import, division, print_function

from marshmallow import Schema, fields


class Error(Schema):
    """Schema for mirror records with errors."""
    recid = fields.Int(required=True)
    collection = fields.Str(required=True)
    valid = fields.Bool(required=True)
    error = fields.Str(required=True, attribute='_errors')

    class Meta:
        strict = True


class ErrorList(Schema):
    """Schema for list of mirror records with errors."""
    data = fields.List(fields.Nested(Error), required=True)

    class Meta:
        strict = True
