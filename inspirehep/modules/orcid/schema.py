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

from HTMLParser import HTMLParser

import dojson

from inspirehep.dojson.utils import force_force_list
from inspirehep.utils.record import get_abstract, get_subtitle, get_title

from .config import ORCID_WORK_TYPES

orcid_overdo = dojson.Overdo()


class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    """ Strips html tags out of a given string.
    """
    if html is None:
        html = ''
    s = MLStripper()
    s.feed(html)
    return s.get_data()


@orcid_overdo.over('title', 'titles')
def title_rule(self, key, value):
    title = get_title({"titles": value})
    if title == '':
        raise KeyError
    subtitle = get_subtitle({"titles": value})
    return {"title": title,
            "subtitle": subtitle}


@orcid_overdo.over('journal-title', 'publication_info')
def publication_rule(self, key, value):
    try:
        return value[0]['journal_title']
    except (TypeError, KeyError):
        pass


@orcid_overdo.over('short-description', 'abstracts')
def abstract_rule(self, key, value):
    return strip_tags(get_abstract({"abstracts": value}))


@orcid_overdo.over('publication-date', 'imprints')
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
    except (TypeError, IndexError, AttributeError):
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
    value = force_force_list(value)
    orcid_authors = []
    for index, author in enumerate(value):
        orcid_authors.append({
            'credit-name': value[index].get('full_name'),
            'contributor-orcid': value[index].get('orcid') if 'orcid' in value[index] else '',
            'contributor-attributes': {
                'contributor-role': 'AUTHOR',
                'contributor-sequence': ('FIRST' if index is 0 else 'ADDITIONAL')
            }
        })
        if index is 19:
            break

    return {"contributor": orcid_authors}


@orcid_overdo.over('type', 'collections')
def work_type_rule(self, key, value):
    work_type = ''
    try:
        for val in value:
            if val['primary'].lower() in ORCID_WORK_TYPES:
                return ORCID_WORK_TYPES[val['primary'].lower()]
            else:
                work_type = 'UNDEFINED'
        return work_type
    except KeyError:
        pass
