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

"""Migrator dumper."""

from __future__ import absolute_import, division, print_function

from marshmallow import ValidationError

from .serializers.schemas.json import ErrorList


def marshmallow_dumper(schema_class):
    """Marshmallow dumper."""
    def schema_dumper(results, many=False):
        try:
            result = schema_class(many=many).dump(results)
        except ValidationError as error:
            raise ValidationError(error.messages)
        return result.data
    return schema_dumper


migrator_error_list_dumper = marshmallow_dumper(ErrorList)
