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


class AuthorAPICoauthors(object):
    """API endpoint for author collection returning co-authors."""

    def serialize(self, pid, record, links_factory=None):
        """Return a list of co-authors for a given author recid.

        :param pid:
            Persistent identifier instance.

        :param record:
            Record instance.

        :param links_factory:
            Factory function for the link generation, which are added to
            the response.
        """
        author_pid = pid.pid_value
        coauthors = {}

        search = LiteratureSearch().query({
            "match": {
                "authors.recid": author_pid
            }
        }).params(
            _source=[
                "authors.full_name",
                "authors.recid",
                "authors.record",
            ]
        )

        for result in search.scan():
            result_source = result.to_dict()['authors']

            for author in result_source:
                try:
                    # Don't add the reference author.
                    if author['recid'] != author_pid:
                        if author['recid'] in coauthors:
                            coauthors[author['recid']]['count'] += 1
                        else:
                            coauthors[author['recid']] = dict(
                                count=1,
                                full_name=author['full_name'],
                                id=author['recid'],
                                record=author['record'],
                            )
                except KeyError:
                    pass

        return json.dumps(coauthors.values())
