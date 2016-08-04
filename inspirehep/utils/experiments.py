
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

from __future__ import absolute_import, division, print_function

from inspirehep.utils.record import get_title
from inspirehep.utils.search import perform_es_search
from inspirehep.utils.template import render_macro_from_template


def render_experiment_contributions(experiment_name):
    """Conference export for single record in datatables format.
    :returns: list
        List of lists where every item represents a datatables row.
        A row consists of
        [conference_name, conference_location, contributions, date]
    """
    return render_contributions(
        experiment_contributions_from_es(experiment_name)
    )


def render_experiment_people(experiment_name):
    """Conference export for single record in datatables format.
    :returns: list
        List of lists where every item represents a datatables row.
        A row consists of
        [conference_name, conference_location, contributions, date]
    """
    return render_people(
        experiment_people_from_es(experiment_name)
    )


def experiment_contributions_from_es(experiment_name):
    """Query ES for conferences in the same series."""
    query = 'accelerator_experiments.experiment:"{}"'.format(experiment_name)
    return perform_es_search(
        query,
        'records-hep',
        sort='-citation_count',
        size=100,
        fields=[
            'control_number',
            'earliest_date',
            'titles',
            'authors',
            'publication_info',
            'citation_count',
            'collaboration'
        ]
    ).hits


def experiment_people_from_es(experiment_name):
    """Query ES for conferences in the same series."""
    query = 'experiments.name:"{}"'.format(experiment_name)
    return perform_es_search(
        query,
        'records-authors'
    ).hits


def render_people(hits):
    """Render a list of conferences to HTML."""

    result = []

    author_html_link = u"<a href='/authors/{recid}'>{name}</a>"

    for hit in hits:
        row = []
        row.append(
            author_html_link.format(
                recid=hit.control_number,
                name=hit.name.preferred_name if hit.name else u''
            )
        )

        result.append(row)

    return result, hits.total


def render_contributions(hits):
    """Render a list of conferences to HTML."""

    result = []

    title_html = "<a href='/literature/{id}'>{name}</a>"

    for hit in hits:
        row = []
        row.append(
            title_html.format(
                id=hit.control_number,
                name=get_title(hit.to_dict()).encode('utf8')
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
