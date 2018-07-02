# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

from flask import current_app as app
import hashlib
from redis import StrictRedis
from StringIO import StringIO

from .converter import OrcidConverter
from .exceptions import EmptyPutcodeError


# Redis client as module-level singleton.
_redis_client = None


def _init_redis_client():
    """
    Note: the `_redis_client` module-level var cannot be initialized at module-load
    time because accessing flask.current_app raises the exception:
    "RuntimeError: Working outside of application context"
    """
    url = app.config.get('CACHE_REDIS_URL')
    global _redis_client
    _redis_client = StrictRedis.from_url(url)


class OrcidCache(object):
    def __init__(self, orcid):
        """
        Orcid cached data.

        Args:
            orcid (string): orcid identifier.
        """
        self.orcid = orcid
        self._cached_hash_value = None
        self._new_hash_value = None
        if not _redis_client:
            _init_redis_client()
        self.redis = _redis_client

    def get_key(self, recid):
        """Return the string 'orcidcache:``orcid_value``:``recid``'"""
        return 'orcidcache:{}:{}'.format(self.orcid, recid)

    def write_work_putcode(self, recid, putcode, inspire_record=None):
        """
        Write the putcode and the hash for the given (orcid, recid).

        Args:
            recid (string): record identifier.
            putcode (string): the putcode used to push the record to ORCID.
            inspire_record (InspireRecord): InspireRecord instance. If provided,
             the hash for the record content is re-computed.
        """
        if not putcode:
            raise EmptyPutcodeError

        data = {'putcode': putcode}

        if inspire_record:
            if not self._new_hash_value:
                self._new_hash_value = _OrcidHasher(inspire_record).compute_hash()
            data['hash'] = self._new_hash_value

        key = self.get_key(recid)
        self.redis.hmset(key, data)

    def read_work_putcode(self, recid):
        """Read the putcode for the given (orcid, recid)."""
        key = self.get_key(recid)
        value = self.redis.hgetall(key)
        self._cached_hash_value = value.get('hash')
        return value.get('putcode')

    def has_work_content_changed(self, recid, inspire_record):
        """
        True if the work content has changed compared to the cached version.

        Args:
            recid (string): record identifier.
            inspire_record (InspireRecord): InspireRecord instance. If provided,
             the hash for the record content is re-computed.
        """
        if not self._cached_hash_value:
            self.read_work_putcode(recid)
        if not self._new_hash_value:
            self._new_hash_value = _OrcidHasher(inspire_record).compute_hash()
        return self._cached_hash_value != self._new_hash_value


class _OrcidHasher(object):
    def __init__(self, inspire_record):
        self.inspire_record = inspire_record

    def compute_hash(self):
        """Generate hash for an ORCID-serialised HEP record.

        Return:
            string: hash of the record
        """
        orcid_record = OrcidConverter(
            self.inspire_record,
            app.config['LEGACY_RECORD_URL_PATTERN']
        )
        xml = orcid_record.get_xml()  # lxml.etree._Element
        return self._hash_xml_element(xml)

    @classmethod
    def _hash_xml_element(cls, element):
        """Compute a hash for XML element comparison.

        Args:
            element (lxml.etree._Element): the XML node.

        Return:
            string: hash
        """
        canonical_string = cls._canonicalize_xml_element(element)
        hash_value = hashlib.sha1(canonical_string)
        return 'sha1:' + hash_value.hexdigest()

    @staticmethod
    def _canonicalize_xml_element(element):
        """Return a string with a canonical representation of the element.

        Args:
            element (lxml.etree._Element): the XML node

        Return:
            string: canonical representation
        """
        element_tree = element.getroottree()
        output_stream = StringIO()
        element_tree.write_c14n(
            output_stream,
            with_comments=False,
            exclusive=True,
        )
        return output_stream.getvalue()
