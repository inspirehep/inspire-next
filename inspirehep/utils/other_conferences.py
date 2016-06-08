
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

from invenio_search import current_search_client as es
from jinja2 import render_template_to_string


def render_conferences_in_the_same_series(recid, seriesname):
        """Conference export for single record in datatables format.
        :returns: list
            List of lists where every item represents a datatables row.
            A row consists of
            [conference_name, conference_location, contributions, date]
        """
        return render_conferences(recid, conferences_in_the_same_series(seriesname))


def conferences_in_the_same_series(seriesname):
    """Query ES for conferences in the same series."""

    es_query = {
        "filter": {
            "bool": {
                "must": [
                    {"match": {"series": seriesname}}
                ]
            }
        }
    }

    conferences_in_series = es.search(
        index='records-conferences',
        doc_type='conferences',
        body=es_query,
        _source=[
            'control_number',
            'title',
            'place',
            'opening_date',
            'closing_date'
        ]
    )['hits']['hits']

    return conferences_in_series


def render_conferences(recid, conferences):
    """Render a list of conferences to HTML."""

    out = []

    for conference in conferences:

        if conference['_source']['control_number'] == recid:
            continue

        row = []
        conference = conference['_source']
        row.append((render_template_to_string(
                    "inspirehep_theme/conferences_in_series.html",
                    record=conference)))
        row.append(conference.get('place', ''))
        row.append('')
        row.append((render_template_to_string(
                    "inspirehep_theme/conferences_in_series_date.html",
                    record=conference)))
        out.append(row)

    return out
