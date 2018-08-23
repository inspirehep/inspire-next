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
