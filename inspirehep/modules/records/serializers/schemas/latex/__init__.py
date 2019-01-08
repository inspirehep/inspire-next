# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

from marshmallow import Schema, fields
from inspire_utils.name import format_name
from ...fields_export import get_best_publication_info

import datetime


class LatexSchema(Schema):
    arxiv_eprints = fields.Raw()
    authors = fields.Method('get_author_names')
    citations = fields.Method('get_citations', default=0)
    collaborations = fields.Method('get_collaborations')
    dois = fields.Raw()
    publication_info = fields.Method('get_publication_info')
    report_numbers = fields.Raw()
    titles = fields.Raw()
    texkeys = fields.Method('get_texkey')
    today = fields.Method('get_current_date')

    def get_citations(self, data):
        citations = data.get('citation_count')

        if citations is None:
            return data.get_citations_count()

        return citations

    def get_author_names(self, data):
        authors = data.get("authors")

        if not authors:
            return fields.missing

        author_names = (format_name(author['full_name'], initials_only=True) for author in authors)
        return [name.replace('. ', '.~') for name in author_names]

    def get_publication_info(self, data):
        publication_info = get_best_publication_info(data)
        if publication_info == {}:
            return fields.missing

        if 'journal_title' in publication_info:
            publication_info['journal_title'] = publication_info['journal_title'].replace('.', '.\\ ')

        if 'page_start' in publication_info:
            if 'page_end' in publication_info:
                publication_info['page_range'] = '{}-{}'.format(publication_info["page_start"], publication_info["page_end"])
            else:
                publication_info['page_range'] = publication_info["page_start"]

        return publication_info

    def get_current_date(self, data):
        now = datetime.datetime.now()
        return now.strftime("%d %b %Y")

    def get_texkey(self, data):
        texkeys = data.get('texkeys')
        if texkeys:
            return texkeys[0]
        return data.get('control_number')

    def get_collaborations(self, data):
        if not data.get('collaborations'):
            return fields.missing

        return [collab['value'] for collab in data.get('collaborations')]
