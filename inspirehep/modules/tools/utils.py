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

"""Utility functions for various tools."""

from __future__ import absolute_import, division, print_function


def authorlist(text):
    """
    Return an author-structure parsed from text
    and optional additional information.
    """

    from inspire_schemas.api import LiteratureBuilder
    from refextract.documents.pdf import replace_undesirable_characters
    from inspirehep.modules.tools.authorlist import create_authors

    builder = LiteratureBuilder()

    text = replace_undesirable_characters(text)
    result = create_authors(text)

    if result.has_key('authors'):
        for fullname, author_affs in result['authors']:
            builder.add_author(
                builder.make_author(fullname, raw_affiliations=author_affs)
            )
        result['authors'] = builder.record['authors']
    return result
