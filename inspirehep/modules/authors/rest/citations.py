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

import json

from inspirehep.modules.search import LiteratureSearch


class AuthorAPICitations(object):
    """API endpoint for author collection returning citations."""

    def serialize(self, pid, record, links_factory=None):
        """Return a list of citations for a given author recid.

        :param pid:
            Persistent identifier instance.

        :param record:
            Record instance.

        :param links_factory:
            Factory function for the link generation, which are added to
            the response.
        """
        author_pid = pid.pid_value
        citations = {}

        search = LiteratureSearch().query({
            "match": {
                "authors.recid": author_pid
            }
        }).params(
            _source=[
                "authors.recid",
                "control_number",
                "self",
            ]
        )

        # For each publication co-authored by a given author...
        for result in search.scan():
            result_source = result.to_dict()

            recid = result_source['control_number']
            authors = set([i['recid'] for i in result_source['authors']])
            citations[recid] = {}

            nested_search = LiteratureSearch().query({
                "match": {
                    "references.recid": recid
                }
            }).params(
                _source=[
                    "authors.recid",
                    "collections",
                    "control_number",
                    "earliest_date",
                    "self",
                ]
            )

            # The source record that is being cited.
            citations[recid]['citee'] = dict(
                id=recid,
                record=result_source['self'],
            )
            citations[recid]['citers'] = []

            # Check all publications, which cite the parent record.
            for nested_result in nested_search.scan():
                nested_result_source = nested_result.to_dict()

                # Not every signature has a recid (at least for demo records).
                try:
                    nested_authors = set(
                        [i['recid'] for i in nested_result_source['authors']]
                    )
                except KeyError:
                    nested_authors = set()

                citation = dict(
                    citer=dict(
                        id=int(nested_result_source['control_number']),
                        record=nested_result_source['self']
                    ),
                    # If at least one author is shared, it's a self-citation.
                    self_citation=len(authors & nested_authors) > 0,
                )

                # Get the earliest date of a citer.
                try:
                    citation['date'] = nested_result_source['earliest_date']
                except KeyError:
                    pass

                # Get status if a citer is published.
                # FIXME: As discussed with Sam, we should have a boolean flag
                #        for this type of information.
                try:
                    citation['published_paper'] = "Published" in [
                        i['primary'] for i in nested_result_source[
                            'collections']]
                except KeyError:
                    citation['published_paper'] = False

                citations[recid]['citers'].append(citation)

        return json.dumps(citations.values())
