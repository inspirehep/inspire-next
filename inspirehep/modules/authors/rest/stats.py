# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import json
from collections import Counter

from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import get_value
from inspirehep.utils.stats import calculate_h_index, calculate_i10_index


class AuthorAPIStats(object):
    """API endpoint for author collection returning statistics."""

    def serialize(self, pid, record, links_factory=None):
        """Return a different metrics for a given author recid.

        :param pid:
            Persistent identifier instance.

        :param record:
            Record instance.

        :param links_factory:
            Factory function for the link generation, which are added to
            the response.
        """
        author_pid = pid.pid_value

        fields = set()
        keywords = []

        statistics = {}
        statistics['citations'] = 0
        statistics['publications'] = 0
        statistics['types'] = {}

        statistics_citations = {}

        search = LiteratureSearch().query({
            "match": {
                "authors.recid": author_pid
            }
        }).params(
            _source=[
                "citation_count",
                "control_number",
                "facet_inspire_doc_type",
                "facet_inspire_subjects",
                "keywords",
            ]
        )

        for result in search.scan():
            result_source = result.to_dict()

            # Increment the count of the total number of publications.
            statistics['publications'] += 1

            # Increment the count of citations.
            citation_count = result_source.get('citation_count', 0)

            statistics['citations'] += citation_count
            statistics_citations[result_source['control_number']] = \
                citation_count

            # Count how many times certain type of publication was published.
            try:
                publication_type = result_source.get(
                    'facet_inspire_doc_type', [])[0]
            except IndexError:
                pass

            if publication_type:
                if publication_type in statistics['types']:
                    statistics['types'][publication_type] += 1
                else:
                    statistics['types'][publication_type] = 1

            # Get fields.
            for field in result_source.get('facet_inspire_subjects', []):
                fields.add(field)

            # Get keywords.
            keywords.extend([
                k for k in force_force_list(
                    get_value(result_source, 'keywords.value'))
                if k != '* Automatic Keywords *'])

        # Calculate h-index together with i10-index.
        statistics['hindex'] = calculate_h_index(statistics_citations)
        statistics['i10index'] = calculate_i10_index(statistics_citations)

        if fields:
            statistics['fields'] = list(fields)

        # Return the top 25 keywords.
        if keywords:
            counter = Counter(keywords)
            statistics['keywords'] = [{
                'count': i[1],
                'keyword': i[0]
            } for i in counter.most_common(25)]

        return json.dumps(statistics)
