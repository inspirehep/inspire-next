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
from inspirehep.utils.record import get_title


class AuthorAPIPublications(object):
    """API endpoint for author collection returning publications."""

    def serialize(self, pid, record, links_factory=None):
        """Return a list of publications for a given author recid.

        :param pid:
            Persistent identifier instance.

        :param record:
            Record instance.

        :param links_factory:
            Factory function for the link generation, which are added to
            the response.
        """
        author_pid = pid.pid_value
        publications = []

        search = LiteratureSearch().query({
            "match": {
                "authors.recid": author_pid
            }
        }).params(
            _source=[
                "accelerator_experiments",
                "earliest_date",
                "citation_count",
                "control_number",
                "facet_inspire_doc_type",
                "publication_info",
                "self",
                "keywords",
                "titles",
            ]
        )

        for result in search.scan():
            result_source = result.to_dict()

            publication = {}
            publication['id'] = int(result_source['control_number'])
            publication['record'] = result_source['self']
            publication['title'] = get_title(result_source)

            # Get the earliest date.
            try:
                publication['date'] = result_source['earliest_date']
            except KeyError:
                pass

            # Get publication type.
            try:
                publication['type'] = result_source.get(
                    'facet_inspire_doc_type', [])[0]
            except IndexError:
                pass

            # Get citation count.
            try:
                publication['citations'] = result_source['citation_count']
            except KeyError:
                pass

            # Get journal.
            try:
                publication['journal'] = {}
                publication['journal']['title'] = result_source.get(
                    'publication_info', [])[0]['journal_title']

                # Get journal id and $self.
                try:
                    publication['journal']['id'] = result_source.get(
                        'publication_info', [])[0]['journal_recid']
                    publication['journal']['record'] = result_source.get(
                        'publication_info', [])[0]['journal_record']
                except KeyError:
                    pass
            except (IndexError, KeyError):
                del publication['journal']

            # Get collaborations.
            collaborations = set()

            for experiment in result_source.get('accelerator_experiments', []):
                collaborations.add(experiment.get('experiment'))

            if collaborations:
                publication['collaborations'] = list(collaborations)

            publications.append(publication)

        return json.dumps(publications)
