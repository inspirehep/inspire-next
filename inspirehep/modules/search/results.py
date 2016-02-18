# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Results class to wrap a query and allow for searching."""

from flask import current_app
from elasticsearch.helpers import scan

class Results(object):

    def __init__(self, query, index=None, doc_type=None, **kwargs):
        self.body = {
            'from': 0,
            'size': 10,
            'query': query,
        }
        self.body.update(kwargs)

        self.index = index
        self.doc_type = doc_type or 'record'

        self._results = None

    @property
    def recids(self):
        from intbitset import intbitset
        from invenio_search import current_search_client
        results = scan(
            current_search_client,
            query={
                'fields': [],
                'query': self.body.get("query")
            },
            index=self.index,
            doc_type=self.doc_type,
        )
        return intbitset([int(r['_id']) for r in results])

    def _search(self):
        from invenio_search import current_search_client

        if self._results is None:
            if current_app.debug:
                import json
                json_body = json.dumps(self.body, indent=2)
                current_app.logger.debug(
                    "index: {0} - doc_type: {1} - query: {2}".format(
                        self.index,
                        self.doc_type,
                        json_body
                    )
                )
            self._results = current_search_client.search(
                index=self.index,
                doc_type=self.doc_type,
                body=self.body,
            )
        return self._results

    def records(self):
        from invenio_records.api import Record
        return [Record(r['_source']) for r in self._search()['hits']['hits']]

    def __len__(self):
        return self._search()['hits']['total']