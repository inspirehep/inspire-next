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

"""Marshmallow JSON schema for a literature entry."""

from __future__ import absolute_import, division, print_function

from .pybtex import PybtexSchema, PublicationInfoSchema
from marshmallow import post_load
from marshmallow.fields import Int, List, Nested


class LatexSchema(PybtexSchema):
    """Schema for Bibtex references."""
    citation_count = Int()
    publication_info_list = List(Nested(PublicationInfoSchema), load_from='publication_info')

    @post_load
    def make_bibtex(self, data):
        texkey, entry = super(LatexSchema, self).make_bibtex(data)
        entry.fields['citation_count'] = data.get('citation_count')
        entry.fields['publication_info_list'] = data.get('publication_info_list')
        entry.fields['primaryClasses'] = ','.join(data.get('arxiv_eprints', {}).get('categories', []))
        return texkey, entry
