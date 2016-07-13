from __future__ import absolute_import

from inspirehep.modules.converttohal import tei

class TEISerializer(object):
    """TEI serializer for records."""

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single tei from a record.
        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for the link generation,
                              which are added to the response.
        """
        return tei.tei_response(record)
