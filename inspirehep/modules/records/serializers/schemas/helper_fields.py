# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

"""Custom Marshmallow field types."""

from __future__ import absolute_import, division, print_function

import re

from marshmallow.fields import Nested, List, Str

from inspirehep.utils.record_getter import get_es_record


class First(List):
    """
    Deserializes only the first element of a list, skipping None elements or entries defined as hidden.
    """
    def _deserialize(self, value, attr, data):
        values = super(First, self)._deserialize(value, attr, data)
        if values:
            for element in values:
                if element is not None or not (isinstance(element, dict) and 'hidden' in element):
                    return element


class FromRecordID(Nested):
    """
    Uses the INSPIRE record ID to fetch the referenced record, and passes it to a nested schema.
    Constructor requires additional parameter 'pid_type' that specifies the type of the record.
    """
    def __init__(self, nested, pid_type, **kwargs):
        super(FromRecordID, self).__init__(nested, **kwargs)
        self.pid_type = pid_type

    def _deserialize(self, value, attr, data):
        record = get_es_record(self.pid_type, value)
        return super(FromRecordID, self)._deserialize(record, attr, data)


class PartialDate(Str):
    """
    Deserializes partial or full dates in ISO-8601, e.g. '2017', '2017-09', '2017-09-12'.
    """
    regex = re.compile(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?.*$")

    def _deserialize(self, value, attr, data):
        value = super(PartialDate, self)._deserialize(value, attr, data)
        match = re.search(PartialDate.regex, value)
        return match.groups()
