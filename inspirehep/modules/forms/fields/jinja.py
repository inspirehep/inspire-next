# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Collection of fields that can be used to render Jinja templates."""

from __future__ import absolute_import, division, print_function

from .. import field_widgets
from ..field_base import INSPIREField

__all__ = ['JinjaField']


class JinjaField(INSPIREField):

    """Generic field that renders a given template."""

    def __init__(self, **kwargs):
        """Create field that displays a given template.

        :param template: path to template that should be used for rendering.
        :type template: str
        """
        defaults = dict(
            widget_classes='form-control',
            widget=field_widgets.JinjaWidget()
        )
        defaults.update(kwargs)
        self.template = defaults.pop('template')
        super(JinjaField, self).__init__(**defaults)
