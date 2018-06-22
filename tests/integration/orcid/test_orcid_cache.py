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

import pytest

from inspirehep.modules.orcid.cache import OrcidCache, OrcidHasher

from factories.db.invenio_records import TestRecordMetadata


@pytest.mark.usefixtures('isolated_app')
class TestOrcidCache(object):
    def setup(self):
        self.recid = 'myrecid'
        self.putcode = 'myputcode'
        self.hash_value = 'myhash'
        self.orcid = '0000-0002-76YY-56XX'
        self.cache = OrcidCache(self.orcid)

    def teardown(self):
        """
        Cleanup the cache after each test (as atm there is no cache isolation).
        """
        key = self.cache._get_key(self.recid)
        self.cache.redis.delete(key)

    def test_new_key(self):
        self.cache.write_record_data(self.recid, self.putcode, self.hash_value)
        putcode, hash_value = self.cache.read_record_data(self.recid)
        assert putcode == self.putcode
        assert hash_value == self.hash_value

    def test_existent_key(self):
        self.cache.write_record_data(self.recid, self.putcode, self.hash_value)
        self.cache.write_record_data(self.recid, '0000', self.hash_value)
        putcode, hash_value = self.cache.read_record_data(self.recid)
        assert putcode == '0000'
        assert hash_value == self.hash_value

    def test_read_non_existent_key(self):
        putcode, hash_value = self.cache.read_record_data(self.recid)
        assert not putcode
        assert not hash_value


@pytest.mark.usefixtures('isolated_app')
class TestOrcidHasher(object):
    def setup(self):
        factory = TestRecordMetadata.create_from_file(__name__, 'test_orcid_hasher_record.json')
        self.record = factory.record_metadata
        self.hash_value = 'sha1:ede49b12e11f5284fdced7596a28791ddf32c8fc'
        self.hasher = OrcidHasher()

    def test_compute_hash(self):
        hash_value = self.hasher.compute_hash(self.record.json)
        assert hash_value == self.hash_value

    def test_edit_ignored_filed(self):
        self.record.json['abstracts'][0]['value'] = 'xxx'
        hash_value = self.hasher.compute_hash(self.record.json)
        assert hash_value == self.hash_value

    def test_edit_considered_filed(self):
        self.record.json['control_number'] = '123'
        hash_value = self.hasher.compute_hash(self.record.json)
        assert hash_value != self.hash_value
