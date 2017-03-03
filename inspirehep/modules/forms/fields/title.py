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

from wtforms import StringField, ValidationError

from ..field_base import INSPIREField

__all__ = ['TitleField']


def validate_title(form, field):
    """Deprecated."""
    import warnings
    warnings.warn("Validator has been deprecated", PendingDeprecationWarning)

    value = field.data or ''
    if value == "" or value.isspace():
        return

    if len(value) <= 4:
        raise ValidationError("This field must have at least 4 characters")


class TitleField(INSPIREField, StringField):

    """Deprecated."""

    def __init__(self, **kwargs):
        """Deprecated."""
        import warnings
        warnings.warn("Field has been deprecated", PendingDeprecationWarning)
        defaults = dict(
            icon='book',
            export_key='title.title',
            widget_classes="form-control"
            # FIXMEvalidators=[validate_title]
        )
        defaults.update(kwargs)
        super(TitleField, self).__init__(**defaults)
