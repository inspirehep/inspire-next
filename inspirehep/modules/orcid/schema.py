# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

import dojson

from dojson import utils

from inspirehep.utils.record import get_abstract, get_subtitle, get_title

orcid_overdo = dojson.Overdo()


@orcid_overdo.over('title', 'titles')
def title_rule(self, key, value):
    title = get_title({"titles": value})
    if title == '':
        raise KeyError
    subtitle = ""
    try:
        subtitle = get_subtitle({"titles": value})
    except KeyError:
        pass
    return {"title": title,
            "subtitle": subtitle}


@orcid_overdo.over('journal_title', 'publication_info')
def publication_rule(self, key, value):
    try:
        return value[0].get('journal_title')
    except (TypeError, KeyError):
        pass


@orcid_overdo.over('short_description', 'abstracts')
def abstract_rule(self, key, value):
    try:
        return get_abstract({"abstracts": value})
    except (TypeError, KeyError):
        pass


@orcid_overdo.over('publication_date', 'imprints')
def date_rule(self, key, value):
    try:
        date = value[0].get('date')
        date = date.split('-')
        final_date = ['', '', '']
        if date[0]:
            final_date[0] = date[0]
        if date[1]:
            final_date[1] = date[1]
        if date[2]:
            final_date[2] = date[2]
        publication_date = {'year': int(final_date[0]),
                            'month': int(final_date[1]),
                            'day': int(final_date[2])
                            }
        return publication_date
    except (TypeError, IndexError):
        pass


@orcid_overdo.over('work_external_identifier', 'arxiv_eprints|dois')
@dojson.utils.for_each_value
def external_id_rule(self, key, value):
    if key == 'dois':
        return{
            'external-identifier-type': 'DOI',
            'external-identifier-id': value.get('value')
        }
    if key == 'arxiv_eprints':
        return {
            'external-identifier-type': 'ARXIV',
            'external-identifier-id': value.get('value')
        }


@orcid_overdo.over('contributors', 'authors')
def authors_rule(self, key, value):
    value = utils.force_list(value)
    orcid_authors = []
    try:
        orcid_authors.append({
            'credit-name': value[0].get('full_name'),
            'contributor-orcid': value[0].get('orcid') if 'orcid' in value[0] else '',
            'contributor-attributes': {
                'contributor-role': 'AUTHOR',
                'contributor-sequence': 'FIRST'
            }
        })
        for author in value[1:]:
            orcid_authors.append({
                'credit-name': author.get('full_name'),
                'contributor-orcid': author.get('orcid') if 'orcid' in author else '',
                'contributor-attributes': {
                    'contributor-role': 'AUTHOR',
                    'contributor-sequence': 'ADDITIONAL'
                }
            })
    except KeyError:
        pass
    return {"contributor": orcid_authors}


@orcid_overdo.over('type', 'collections')
def work_type_rule(self, key, value):
    work_types = {
        "book": "BOOK",
        "conferencepaper": "CONFERENCE_PAPER",
        "proceedings": "BOOK",
        "preprint": "WORKING_PAPER",
        "note": "WORKING_PAPER",
        "published": "JOURNAL_ARTICLE",
        "thesis": "DISSERTATION",
        "lectures": "LECTURE_SPEECH",
        "bookchapter": "BOOK_CHAPTER",
        "report": "REPORT"
    }
    work_type = ''
    try:
        for val in value:
            if val['primary'].lower() in work_types:
                return work_types[val['primary'].lower()]
            else:
                work_type = 'UNDEFINED'
        return work_type
    except KeyError:
        pass
