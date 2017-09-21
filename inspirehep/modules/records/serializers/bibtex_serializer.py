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

"""BibTex serializer for records."""

from __future__ import absolute_import, division, print_function

from .pybtex_plugins import BibtexWriter
from .pybtex_serializer_base import PybtexSerializerBase
from .schemas.bibtex import BibtexSchema


class BIBTEXSerializer(PybtexSerializerBase):
    """BibTex serializer for records."""

    def get_writer(self):
        return BibtexWriter()

    def get_schema(self):
        return BibtexSchema()

    def create_bibliography(self, record_list):
        bibtex_string = super(BIBTEXSerializer, self).create_bibliography(record_list)
        # Pybtex escapes '%' in Bibtex, however we don't want that to happen in SLACcitations.
        # The odds of two consecutive '%' in other fields are so low, that it's reasonable to
        # do a simple replacement on the whole bibtex string here:
        return bibtex_string.replace(r'\%\%', '%%')
