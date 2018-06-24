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


class OrcidCache(object):
    def __init__(self, orcid):
        redis_url = app.config.get('CACHE_REDIS_URL')
        self.redis = StrictRedis.from_url(redis_url)
        self.orcid = orcid

    def _get_key(self, recid):
        """Return the string 'orcidcache:``orcid_value``:``recid``'"""
        return 'orcidcache:{}:{}'.format(self.orcid, recid)

    def write_record_data(self, recid, putcode, hash_value=None):
        """
        Write the putcode and the hash for the given (orcid, recid).

        Args:
            recid(int): inspire record's id.
            putcode(string): the putcode used to push the record to ORCID.
            hash_value(Optional[string]): hashed ORCID record content.
        """
        if not putcode:
            raise EmptyPutcodeError

        key = self._get_key(recid)
        value = {'putcode': putcode}
        if hash_value:
            value['hash'] = hash_value
        self.redis.hmset(key, value)

    def read_record_data(self, recid):
        """
        Read the putcode and the hash for the given (orcid, recid).

        Args:
            recid(int): inspire record's id.
        """
        key = self._get_key(recid)
        value = self.redis.hgetall(key)
        return value.get('putcode'), value.get('hash')


class OrcidHasher(object):
    def compute_hash(self, record):
        """Generate hash for an ORCID-serialised HEP record

        Args:
            record (dict): HEP record

        Returns:
            string: hash of the record
        """
        orcid_rec = OrcidConverter(record, app.config['LEGACY_RECORD_URL_PATTERN'])
        return self._hash_xml_element(orcid_rec.get_xml())

    def _hash_xml_element(self, element):
        """Compute a hash for XML element comparison.

        Args:
            element (lxml.etree._Element): the XML node

        Return:
            string: hash
        """
        canonical_string = self._canonicalize_xml_element(element)
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
