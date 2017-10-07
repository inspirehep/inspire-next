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

"""Deprecated."""

from __future__ import absolute_import, division, print_function

import warnings

from wtforms import StringField

from ..field_base import INSPIREField

__all__ = ['TitleField']


class TitleField(INSPIREField, StringField):

    """Deprecated."""

    def __init__(self, **kwargs):
        """Deprecated."""
        warnings.warn("Field has been deprecated", PendingDeprecationWarning)
        defaults = dict(
            icon='book',
            export_key='title.title',
            widget_classes="form-control"
        )
        defaults.update(kwargs)
        super(TitleField, self).__init__(**defaults)
