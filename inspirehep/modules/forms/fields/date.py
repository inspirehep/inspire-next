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

from __future__ import absolute_import, division, print_function

from datetime import date, datetime

import six
from wtforms import DateField
from wtforms.validators import optional

from ..field_base import INSPIREField

__all__ = ['Date']


class Date(INSPIREField, DateField):
    def __init__(self, **kwargs):
        defaults = dict(
            icon='calendar',
            validators=[optional()],
            widget_classes="form-control"
        )
        defaults.update(kwargs)
        super(Date, self).__init__(**defaults)

    def process_data(self, value):
        """
        Called when loading data from Python (incoming objects can be either
        datetime objects or strings, depending on if they are loaded from
        an JSON or Python objects).
        """
        if isinstance(value, six.string_types):
            self.object_data = datetime.strptime(value, self.format).date()
        elif isinstance(value, datetime):
            self.object_data = value.date()
        elif isinstance(value, date):
            self.object_data = value
        # Be sure to set both self.object_data and self.data due to internals
        # of Field.process() and draft_form_process_and_validate().
        self.data = self.object_data

    @property
    def json_data(self):
        """
        Serialize data into JSON serializalbe object
        """
        # Just use _value() to format the date into a string.
        if self.data:
            return self.data.strftime(self.format)  # pylint: disable-msg=
        return None
