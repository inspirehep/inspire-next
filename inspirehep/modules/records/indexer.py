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

from invenio_indexer.api import RecordIndexer

from inspirehep.modules.records.api import InspireRecord


class InspireRecordIndexer(RecordIndexer):
    def index_by_id(self, record_uuid):
        """
        Index a record by record identifier
        Args:
            record_uuid: Record uuid
        """
        return self.index(InspireRecord.get_record(record_uuid))

    def delete_by_id(self, record_uuid):
        """Delete record from index by record identifier."""
        self.delete(InspireRecord.get_record(record_uuid))

    def _delete_action(self, payload):
        """
        Bulk delete action.
        Args:
            payload: Decoded message body.

        Returns:
            Dictionary defining an Elasticsearch bulk 'delete' action.

        """
        index, doc_type = payload.get('index'), payload.get('doc_type')
        if not (index and doc_type):
            record = InspireRecord.get_record(payload['id'])
            index, doc_type = self.record_to_index(record)

        return {
            '_op_type': 'delete',
            '_index': index,
            '_type': doc_type,
            '_id': payload['id'],
        }

    def _index_action(self, payload):
        """
        Bulk index action.
        Args:
            payload: Decoded message body.

        Returns:
            Dictionary defining an Elasticsearch bulk 'index' action.

        """
        record = InspireRecord.get_record(payload['id'])
        index, doc_type = self.record_to_index(record)

        return {
            '_op_type': 'index',
            '_index': index,
            '_type': doc_type,
            '_id': str(record.id),
            '_version': record.revision_id,
            '_version_type': self._version_type,
            '_source': self._prepare_record(record, index, doc_type),
        }
