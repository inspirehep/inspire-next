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

"""LaTeX (EU) serializer for records."""

from __future__ import absolute_import, division, print_function

from .pybtex_plugins import PlainTextWriter
from .pybtex_serializer_base import PybtexSerializerBase
from .schemas.plain import PlainSchema


class HTMLWriter(PlainTextWriter):
    RECORDS_SEPARATOR = '<br /><br />'

    def get_template_src(self):
        return 'inspirehep_theme/records/html_cv.html'


class CVHTMLSerializer(PybtexSerializerBase):
    """Plaintext serializer for records."""

    def get_writer(self):
        return HTMLWriter()

    def get_schema(self):
        return PlainSchema()
