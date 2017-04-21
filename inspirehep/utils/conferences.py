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

from __future__ import absolute_import, division, print_function

from inspirehep.modules.search import ConferencesSearch, LiteratureSearch
from inspirehep.utils.jinja2 import render_template_to_string
from inspirehep.utils.record import get_title
from inspirehep.utils.template import render_macro_from_template


def render_conferences_in_the_same_series(recid, seriesname):
    """Conference export for single record in datatables format.
    :returns: list
    List of lists where every item represents a datatables row.
    A row consists of [conference_name, conference_location, contributions, date]
    """
    return render_conferences(
        recid,
        conferences_in_the_same_series_from_es(seriesname)
    )


def render_conferences_contributions(cnum):
    """Conference export for single record in datatables format.
    :returns: list
    List of lists where every item represents a datatables row.
    A row consists of [conference_name, conference_location, contributions, date]
    """
    return render_contributions(conferences_contributions_from_es(cnum))


def conferences_in_the_same_series_from_es(seriesname):
    """Query ES for conferences in the same series."""
    query = 'series:"{}"'.format(seriesname)
    return ConferencesSearch().query_from_iq(
        query
    ).params(
        _source=[
            'control_number',
            'titles',
            'address',
            'opening_date',
            'closing_date'
        ]
    ).sort("-opening_date").execute().hits


def conferences_contributions_from_es(cnum):
    """Query ES for conferences in the same series."""
    query = 'cnum:"{}"'.format(cnum)
    return LiteratureSearch().query_from_iq(
        query
    ).params(
        size=100,
        _source=[
            'control_number',
            'earliest_date',
            'titles',
            'authors',
            'publication_info',
            'citation_count',
            'collaboration'
        ]
    ).sort('-citation_count').execute().hits


def render_conferences(recid, conferences):
    """Render a list of conferences to HTML."""

    out = []

    for conference in conferences:

        if conference['control_number'] == recid:
            conferences.total = conferences.total - 1
            continue

        row = []
        conference_html = u'<a href="/conferences/{recid}">{title}</a>'.format(
            recid=conference.control_number,
            title=conference.titles[0].title
        )
        row.append(conference_html)
        row.append(conference['address'][0]['original_address'])
        row.append('')
        row.append((render_template_to_string(
                    "inspirehep_theme/conferences_in_series_date.html",
                    record=conference.to_dict())))
        out.append(row)

    return out, conferences.total


def render_contributions(hits):
    """Render a list of conferences to HTML."""

    result = []

    title_html = u"<a href='/literature/{id}'>{name}</a>"

    for hit in hits:
        row = []
        row.append(
            title_html.format(
                id=hit.control_number,
                name=get_title(hit.to_dict())
            )
        )
        ctx = {
            'record': hit.to_dict(),
            'is_brief': 'true',
            'number_of_displayed_authors': 1,
            'show_affiliations': 'false',
            'collaboration_only': 'true'
        }
        row.append(render_macro_from_template(
            name="render_record_authors",
            template="inspirehep_theme/format/record/Inspire_Default_HTML_general_macros.tpl",
            ctx=ctx
        )
        )
        try:
            row.append(hit.publication_info[0].journal_title)
        except AttributeError:
            row.append('')

        try:
            row.append(hit.citation_count)
        except AttributeError:
            row.append(0)

        result.append(row)

    return result, hits.total
