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

from .writers import LatexWriter
from .pybtex_serializer_base import PybtexSerializerBase
from .schemas.latex import LatexSchema


class LatexCVWriter(LatexWriter):
    def __init__(self):
        self.style = 'latex_cv'

    def write_postamble(self, bib_data):
        return ""

    def write_preamble(self, bib_data):
        return ""


class CVLatexSerializer(PybtexSerializerBase):
    """Latex (EU) serializer for records."""

    def get_writer(self):
        return LatexCVWriter()

    def get_schema(self):
        return LatexSchema()
